from compliance_engine import ComplianceEngine, IngestionPipeline, ComplianceStatus
import io
import sys

def test_validate_ingestion_pipeline_compliant():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], True)
    assert engine.validate_ingestion_pipeline(pipeline) == ComplianceStatus.COMPLIANT

def test_validate_ingestion_pipeline_non_compliant():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], False)
    assert engine.validate_ingestion_pipeline(pipeline) == ComplianceStatus.NON_COMPLIANT

def test_generate_compliance_report():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], True)
    engine.generate_compliance_report(pipeline, ComplianceStatus.COMPLIANT)
    assert len(engine.compliance_report) == 1

def test_run_ingestion_pipeline_compliant():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], True)
    assert engine.run_ingestion_pipeline(pipeline, True)

def test_run_ingestion_pipeline_non_compliant():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], False)
    assert not engine.run_ingestion_pipeline(pipeline, True)

def test_print_compliance_report():
    engine = ComplianceEngine()
    pipeline = IngestionPipeline("test_pipeline", ["PHI data"], True)
    engine.generate_compliance_report(pipeline, ComplianceStatus.COMPLIANT)
    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    engine.print_compliance_report()
    sys.stdout = sys.__stdout__
    assert capturedOutput.getvalue().strip() == '[{"pipeline_name": "test_pipeline", "status": "COMPLIANT"}]'
