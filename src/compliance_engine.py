import argparse
import json
from dataclasses import dataclass
from enum import Enum
from typing import List

class ComplianceStatus(Enum):
    COMPLIANT = 1
    NON_COMPLIANT = 2

@dataclass
class IngestionPipeline:
    name: str
    data: List[str]
    encrypted: bool

class ComplianceEngine:
    def __init__(self):
        self.compliance_report = []

    def validate_ingestion_pipeline(self, pipeline: IngestionPipeline) -> ComplianceStatus:
        if not pipeline.encrypted and any("PHI" in data for data in pipeline.data):
            return ComplianceStatus.NON_COMPLIANT
        return ComplianceStatus.COMPLIANT

    def generate_compliance_report(self, pipeline: IngestionPipeline, status: ComplianceStatus):
        self.compliance_report.append({
            "pipeline_name": pipeline.name,
            "status": status.name
        })

    def run_ingestion_pipeline(self, pipeline: IngestionPipeline, compliant: bool) -> bool:
        status = self.validate_ingestion_pipeline(pipeline)
        if compliant and status == ComplianceStatus.NON_COMPLIANT:
            return False
        self.generate_compliance_report(pipeline, status)
        return True

    def print_compliance_report(self):
        print(json.dumps(self.compliance_report))

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--compliant", action="store_true")
        args = parser.parse_args()
        pipeline = IngestionPipeline("test_pipeline", ["PHI data"], False)
        if self.run_ingestion_pipeline(pipeline, args.compliant):
            self.print_compliance_report()

if __name__ == "__main__":
    engine = ComplianceEngine()
    engine.main()
