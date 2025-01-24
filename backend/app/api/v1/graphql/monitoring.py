from typing import List, Optional
from graphql import GraphQLResolveInfo
import strawberry
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.task import Task
from app.services.monitoring_analysis_service import MonitoringAnalysisService

@strawberry.type
class TechnicalDetails:
    component: str
    current_state: str
    desired_state: str
    eol_date: Optional[str] = None
    days_until_eol: Optional[int] = None
    is_eol: bool = False

@strawberry.type
class MonitoringFinding:
    type: str
    description: str
    severity: str
    confidence: float
    confidence_rationale: str
    estimated_hours: float
    priority: str
    technical_details: TechnicalDetails
    recommended_action: str
    dependencies: List[str]
    risks: List[str]
    deadline: Optional[str] = None

@strawberry.type
class RiskFactors:
    security_risk: float
    performance_risk: float
    compliance_risk: float
    update_risk: float

@strawberry.type
class RiskAssessment:
    overall_risk: str
    confidence: float
    rationale: str
    immediate_actions_required: bool
    factors: RiskFactors

@strawberry.type
class MonitoringAnalysis:
    system_health: str
    context: str
    severity_level: str
    confidence_score: float
    findings: List[MonitoringFinding]
    total_estimated_hours: float
    risk_assessment: RiskAssessment

@strawberry.input
class MonitoringDataInput:
    system: strawberry.scalars.JSON

@strawberry.type
class Task:
    id: int
    project_id: int
    description: str
    estimated_hours: float
    actual_hours: Optional[float]
    status: str
    priority: str
    confidence_score: float
    confidence_rationale: str
    finding_type: Optional[str]
    technical_details: Optional[strawberry.scalars.JSON]
    risks: Optional[List[str]]
    severity: Optional[str]

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def analyze_system(
        self,
        info: GraphQLResolveInfo,
        system_id: strawberry.ID,
        monitoring_data: MonitoringDataInput
    ) -> MonitoringAnalysis:
        db: Session = info.context["db"]
        current_user: User = info.context["user"]
        
        # Initialize monitoring service
        monitoring_service = MonitoringAnalysisService()
        
        # Analyze monitoring data
        analysis_result = await monitoring_service.analyze_monitoring_data(
            monitoring_data=monitoring_data.system
        )
        
        return analysis_result

    @strawberry.mutation
    async def create_monitoring_tasks(
        self,
        info: GraphQLResolveInfo,
        system_id: strawberry.ID,
        findings: List[MonitoringFinding]
    ) -> List[Task]:
        db: Session = info.context["db"]
        current_user: User = info.context["user"]
        
        # Initialize monitoring service
        monitoring_service = MonitoringAnalysisService()
        
        # Convert findings to tasks
        tasks = monitoring_service.convert_findings_to_tasks(
            findings=findings,
            project_id=int(system_id),
            db=db
        )
        
        return tasks

@strawberry.type
class Query:
    @strawberry.field
    def monitoring_tasks(
        self,
        info: GraphQLResolveInfo,
        system_id: Optional[strawberry.ID] = None,
        status: Optional[str] = None
    ) -> List[Task]:
        db: Session = info.context["db"]
        current_user: User = info.context["user"]
        
        query = db.query(Task)
        
        if system_id:
            query = query.filter(Task.project_id == int(system_id))
        if status:
            query = query.filter(Task.status == status)
            
        return query.all()

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
