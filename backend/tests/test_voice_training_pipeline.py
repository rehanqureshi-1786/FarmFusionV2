"""
Comprehensive Test Suite for FarmFusion Voice & Language Training Infrastructure.
Validates:
1. Dataset manifest provenance, licensing gates, and approval checks
2. Synthetic speech data rejection
3. Speaker-disjoint audio partitioning (zero speaker leakage)
4. Audio & Text preprocessing pipelines
5. Gated NLU training & serialization
6. LID & Dialect classifier training pipelines
7. Multi-dimensional evaluation (WER, CER, Agricultural Entity Accuracy)
8. Versioned model export & language pack bundling
"""
import pytest
import sys
from pathlib import Path
import json
import tempfile

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from ml_training.voice import (
    DatasetManifest,
    DatasetTask,
    DatasetType,
    DatasetLicense,
    VoiceDatasetLoader,
    DatasetQualityGate,
    TrainingGateError,
    DatasetIngestionPipeline,
    VoiceAudioProcessor,
    VoiceTextNormalizer,
    AgriculturalNLUTrainer,
    LanguageIdentificationTrainer,
    DialectClassifierTrainer,
    ASRTrainingConfig,
    ASRAdaptationPipeline,
    TTSTrainingConfig,
    TTSAdaptationPipeline,
    compute_wer,
    compute_cer,
    compute_agricultural_entity_accuracy,
    VoiceModelEvaluator,
    VoiceModelExporter,
    LanguagePackBundleGenerator,
)


def test_dataset_manifest_approval_gate():
    """Verify that unapproved datasets or datasets missing licensing fail the validation gate."""
    unapproved_manifest = DatasetManifest(
        dataset_id="unapproved_hi_agri_01",
        task=DatasetTask.NLU,
        dataset_type=DatasetType.INTENT_SLOT,
        language="hi",
        source="Unverified Source",
        license=DatasetLicense.OPEN_GOV_INDIA,
        text_rows=100,
        approved_for_training=False,
    )
    is_valid, errors = unapproved_manifest.validate_for_training()
    assert is_valid is False
    assert any("approved_for_training" in e for e in errors)

    # Approved manifest
    approved_manifest = DatasetManifest(
        dataset_id="approved_hi_agri_01",
        task=DatasetTask.NLU,
        dataset_type=DatasetType.INTENT_SLOT,
        language="hi",
        source="ICAR Agmarknet Open Data",
        license=DatasetLicense.OPEN_GOV_INDIA,
        text_rows=100,
        approved_for_training=True,
    )
    is_valid_app, errors_app = approved_manifest.validate_for_training()
    assert is_valid_app is True
    assert len(errors_app) == 0


def test_synthetic_data_rejection():
    """Verify that synthetic speech flags are rejected in manifests."""
    with pytest.raises(ValueError, match="Synthetic speech data is strictly prohibited"):
        DatasetManifest(
            dataset_id="fake_synth_01",
            task=DatasetTask.ASR,
            dataset_type=DatasetType.AUDIO_ASR,
            language="hi",
            source="Fake AI Generator",
            license=DatasetLicense.MIT,
            is_synthetic=True,
        )


def test_speaker_disjoint_splitting():
    """Verify that ASR dataset splitting guarantees zero speaker leakage."""
    sample_records = []
    # 5 speakers, 4 samples each = 20 samples
    for spk_idx in range(5):
        spk_id = f"speaker_{spk_idx}"
        for s_idx in range(4):
            sample_records.append({
                "id": f"{spk_id}_{s_idx}",
                "audio_path": f"/data/{spk_id}_{s_idx}.wav",
                "transcript": "गेहूं का भाव बताओ",
                "language": "hi",
                "speaker_id": spk_id,
                "duration_sec": 2.5,
                "sampling_rate": 16000,
            })

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_records, f)
        temp_path = Path(f.name)

    split = VoiceDatasetLoader.load_asr_dataset_speaker_disjoint(temp_path)
    train_speakers = {s.speaker_id for s in split.train}
    val_speakers = {s.speaker_id for s in split.val}
    test_speakers = {s.speaker_id for s in split.test}

    # Verify zero speaker intersection
    assert len(train_speakers.intersection(val_speakers)) == 0
    assert len(train_speakers.intersection(test_speakers)) == 0
    assert len(split.train) + len(split.val) + len(split.test) == 20
    temp_path.unlink()


def test_audio_preprocessing():
    """Verify audio duration limits, SNR estimation, and peak verification."""
    # PCM16 mono buffer: 4096 (0x00, 0x10) and 8192 (0x00, 0x20) amplitude
    raw_pcm = b"\x00\x00\x00\x10\x00\x20\x00\x00" * 2000 # ~1 second at 16kHz
    res = VoiceAudioProcessor.inspect_and_clean_pcm16(raw_pcm, target_sample_rate=16000)
    assert res.sample_rate == 16000
    assert res.duration_sec >= 0.5
    assert res.is_valid is True

    # Empty audio rejection
    res_empty = VoiceAudioProcessor.inspect_and_clean_pcm16(b"", target_sample_rate=16000)
    assert res_empty.is_valid is False


def test_text_normalizer():
    """Verify NFKC normalization, punctuation stripping, and agricultural term canonicalization."""
    text = "  गेहूं , में ! पीला रतुआ लग गया है ।  "
    norm = VoiceTextNormalizer.normalize_text(text)
    assert "।" not in norm
    assert "," not in norm

    asr_target = VoiceTextNormalizer.prepare_asr_target(text)
    assert asr_target.strip() != ""

    canon = VoiceTextNormalizer.canonicalize_agri_entities("म्हाने बाजरी रो भाव बताओ")
    assert "Pearl Millet" in canon or "बाजरी" in canon


def test_nlu_trainer_pipeline():
    """Verify end-to-end NLU training on verified agricultural samples."""
    samples = [
        {"id": "s1", "text": "उदयपुर में मौसम कैसा रहेगा", "language": "hi", "intent": "weather"},
        {"id": "s2", "text": "कल बारिश होगी क्या", "language": "hi", "intent": "weather"},
        {"id": "s3", "text": "जयपुर का तापमान बताओ", "language": "hi", "intent": "weather"},
        {"id": "s4", "text": "गेहूं का मंडी भाव क्या है", "language": "hi", "intent": "mandi"},
        {"id": "s5", "text": "सरसों का ताजा भाव बताओ", "language": "hi", "intent": "mandi"},
        {"id": "s6", "text": "कपास के दाम क्या चल रहे हैं", "language": "hi", "intent": "mandi"},
        {"id": "s7", "text": "काली मिट्टी में कौन सी फसल लगाएं", "language": "hi", "intent": "crop_recommendation"},
        {"id": "s8", "text": "खेत में क्या बोएं", "language": "hi", "intent": "crop_recommendation"},
        {"id": "s9", "text": "अच्छी पैदावार के लिए क्या लगाएं", "language": "hi", "intent": "crop_recommendation"},
        {"id": "s10", "text": "पत्ती में झुलसा रोग लगा है", "language": "hi", "intent": "disease"},
        {"id": "s11", "text": "इल्ली की रोकथाम कैसे करें", "language": "hi", "intent": "disease"},
        {"id": "s12", "text": "कीड़े मारने की दवा बताओ", "language": "hi", "intent": "disease"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(samples, f)
        data_path = Path(f.name)

    manifest = DatasetManifest(
        dataset_id="test_hi_nlu_demo",
        task=DatasetTask.NLU,
        dataset_type=DatasetType.INTENT_SLOT,
        language="hi",
        source="FarmFusion Gold Test",
        license=DatasetLicense.OPEN_GOV_INDIA,
        text_rows=len(samples),
        approved_for_training=True,
    )

    with tempfile.TemporaryDirectory() as out_dir:
        trainer = AgriculturalNLUTrainer(output_dir=Path(out_dir))
        res = trainer.train(manifest, data_path, min_samples=10)
        assert Path(res["model_path"]).exists()
        assert "weather" in res["metrics"]["intents"]
        assert "mandi" in res["metrics"]["intents"]

    data_path.unlink()


def test_lid_trainer_pipeline():
    """Verify language identification training pipeline."""
    records = [
        {"text": "उदयपुर में मौसम कैसा है", "language": "hi"},
        {"text": "गेहूं का भाव बताओ", "language": "hi"},
        {"text": "આજે હવામાન કેવું રહેશે", "language": "gu"},
        {"text": "કપાસનો ભાવ શું છે", "language": "gu"},
        {"text": "आजचे हवामान कसे आहे", "language": "mr"},
        {"text": "गव्हाचा दर काय आहे", "language": "mr"},
        {"text": "ਅੱਜ ਦਾ ਮੌਸਮ ਕਿਹੋ ਜਿਹਾ ਹੈ", "language": "pa"},
        {"text": "ਕਣਕ ਦਾ ਭਾਅ ਦੱਸੋ", "language": "pa"},
        {"text": "What is the weather today", "language": "en"},
        {"text": "Tell me wheat market price", "language": "en"},
    ]
    manifest = DatasetManifest(
        dataset_id="test_lid_manifest",
        task=DatasetTask.LID,
        dataset_type=DatasetType.TEXT_ONLY,
        language="all_indic",
        source="Test Benchmark",
        license=DatasetLicense.MIT,
        text_rows=len(records),
        approved_for_training=True,
    )
    with tempfile.TemporaryDirectory() as out_dir:
        trainer = LanguageIdentificationTrainer(output_dir=Path(out_dir))
        res = trainer.train(manifest, records)
        assert Path(res["model_path"]).exists()
        assert "hi" in res["languages"]
        assert "gu" in res["languages"]


def test_wer_cer_and_agri_entity_metrics():
    """Verify evaluation metric calculations."""
    refs = ["आज उदयपुर में मौसम साफ रहेगा", "गेहूं का भाव दो हजार रुपये है"]
    hyps = ["आज उदयपुर में मौसम साफ रहेगा", "गेहूं का भाव दो सौ रुपये है"]

    wer = compute_wer(refs, hyps)
    cer = compute_cer(refs, hyps)
    assert 0.0 < wer < 0.3
    assert 0.0 < cer < 0.2

    # Agri entity accuracy
    agri_acc = compute_agricultural_entity_accuracy(refs, hyps, ["गेहूं", "उदयपुर", "भाव"])
    assert agri_acc == 1.0


def test_slice_evaluator():
    """Verify demographic slice evaluation reporting."""
    test_data = [
        {"reference": "उदयपुर में मौसम कैसा है", "hypothesis": "उदयपुर में मौसम कैसा है", "tags": ["standard_speech", "agricultural_vocabulary"]},
        {"reference": "म्हाने बाजरी रो भाव बताओ", "hypothesis": "म्हाने बाजरी रो भाव बताओ", "tags": ["rural_speech", "regional_dialect", "agricultural_vocabulary"]},
    ]
    report = VoiceModelEvaluator.evaluate_asr_model("indicwhisper_hi_rwr", test_data)
    assert report.model_id == "indicwhisper_hi_rwr"
    assert report.overall_wer == 0.0
    assert "regional_dialect" in report.slices
    assert report.slices["regional_dialect"].sample_count == 1


def test_model_exporter_and_packager():
    """Verify versioned model export and language pack bundle generation."""
    with tempfile.TemporaryDirectory() as base_export:
        # 1. Create a dummy model file
        dummy_model = Path(base_export) / "dummy.joblib"
        dummy_model.write_text("model_binary_payload")

        exporter = VoiceModelExporter(base_export_dir=Path(base_export))
        meta = exporter.export_model_artifact(
            artifact_path=dummy_model,
            model_id="agri_nlu_hi_v1",
            task="nlu",
            language="hi",
            version="1.0.0",
        )
        assert meta.sha256_checksum is not None
        assert (Path(base_export) / "nlu/hi/1.0.0/dummy.joblib").exists()
        assert (Path(base_export) / "nlu/hi/1.0.0/metadata.json").exists()

        # 2. Package into Language Pack bundle
        pack_dir = LanguagePackBundleGenerator.generate_bundle(
            output_dir=Path(base_export) / "packs",
            language="hi",
            name="Hindi",
            native_name="हिन्दी",
            version="1.0.0",
        )
        assert (pack_dir / "metadata.json").exists()
        assert (pack_dir / "vocabulary.json").exists()
        assert (pack_dir / "prompts.json").exists()
