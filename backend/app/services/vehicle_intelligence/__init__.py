from backend.app.services.vehicle_intelligence.source_registry import SourceRegistry, BaseSourceAdapter, MockAutomotiveProvider
from backend.app.services.vehicle_intelligence.extraction_service import ExtractionService
from backend.app.services.vehicle_intelligence.normalization_service import NormalizationService
from backend.app.services.vehicle_intelligence.validation_service import ValidationService
from backend.app.services.vehicle_intelligence.deduplication_service import DeduplicationService
from backend.app.services.vehicle_intelligence.search_service import SearchService
from backend.app.services.vehicle_intelligence.update_service import UpdateService
from backend.app.services.vehicle_intelligence.discovery_service import DiscoveryService
from backend.app.services.vehicle_intelligence.scheduler import VehicleIntelligenceScheduler
from backend.app.services.vehicle_intelligence.vehiclesdb_service import VehiclesDBService
from backend.app.services.vehicle_intelligence.wikimedia_image_service import WikimediaImageService
from backend.app.services.vehicle_intelligence.wikidata_enricher import WikidataEnricher
from backend.app.services.vehicle_intelligence.indian_government_data_service import IndianGovernmentDataService
from backend.app.services.vehicle_intelligence.oem_adapters import OEMSpecificationRegistry
from backend.app.services.vehicle_intelligence.meterapp_service import MeterAppService

__all__ = [
    "SourceRegistry",
    "BaseSourceAdapter",
    "MockAutomotiveProvider",
    "ExtractionService",
    "NormalizationService",
    "ValidationService",
    "DeduplicationService",
    "SearchService",
    "UpdateService",
    "DiscoveryService",
    "VehicleIntelligenceScheduler",
    "VehiclesDBService",
    "WikimediaImageService",
    "WikidataEnricher",
    "IndianGovernmentDataService",
    "OEMSpecificationRegistry",
    "MeterAppService"
]

