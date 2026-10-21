"""Heuristic lead temperature / priority analysis."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

from models.lead import Lead

Temperature = Literal["hot", "warm", "cold"]


class LeadAnalysis(BaseModel):
    temperature: Temperature
    temperature_label: str
    score: int = Field(ge=0, le=100)
    is_urgent: bool
    worth_time: bool
    worth_time_label: str
    needs_personal_manager: bool
    department: str
    department_label: str
    reasons: list[str] = Field(default_factory=list)


class ScoredLead(Lead):
    analysis: LeadAnalysis


class LeadQueueStats(BaseModel):
    total: int = 0
    hot: int = 0
    warm: int = 0
    cold: int = 0
    urgent: int = 0
    with_manager: int = 0
    avg_score: float = 0
    by_department: dict[str, int] = Field(default_factory=dict)


_URGENT_RE = re.compile(
    r"срочн\w*|asap|завтра|сегодня|"
    r"эт(у|ой)\s*недел|"
    r"как\s*можно\s*быстрее|deadline|горит",
    re.IGNORECASE,
)
_NOT_URGENT_RE = re.compile(
    r"не\s*срочн\w*",
    re.IGNORECASE,
)
_MANAGER_RE = re.compile(
    r"директор|руковод|owner|ceo|founder|"
    r"управляющ|менеджер|владел",
    re.IGNORECASE,
)
_LARGE_RE = re.compile(
    r"крупн|холдинг|корпорац|enterprise|"
    r"100\+|500\+|1000\+|парк",
    re.IGNORECASE,
)


def _parse_budget(raw: str | None) -> int:
    if not raw:
        return 0
    digits = re.sub(r"\D", "", str(raw))
    if not digits:
        return 0
    try:
        return int(digits)
    except ValueError:
        return 0


def _text(*parts: str | None) -> str:
    return " ".join(p for p in parts if p) or ""


def _department(lead: Lead, budget: int) -> tuple[str, str]:
    product = (lead.interested_product or lead.task_type or "").lower()
    niche = (lead.niche or "").lower()
    company = (lead.company_size or "") + " " + (lead.business_info or "")

    if _LARGE_RE.search(company) or "флот" in niche:
        return "fleet", "Корпоративный / флот"
    if any(k in product for k in ("bose", "акустик", "музык")):
        return "audio", "Аудио / мультимедиа"
    if any(k in product for k in ("покраск", "аэрограф", "цвет")):
        return "paint", "Покраска / аэрография"
    if budget >= 1_500_000:
        return "premium", "Премиум-продажи"
    return "sales", "Продажи"


def analyze_lead(lead: Lead) -> LeadAnalysis:
    budget = _parse_budget(lead.budget)
    blob = _text(
        lead.deadline,
        lead.comments,
        lead.need_volume,
        lead.task_volume,
        lead.role,
        lead.company_size,
        lead.niche,
    )
    reasons: list[str] = []
    score = 35

    cleaned = _NOT_URGENT_RE.sub(" ", blob)
    is_urgent = bool(_URGENT_RE.search(cleaned))
    if is_urgent:
        score += 28
        reasons.append("В заявке есть маркеры срочности")

    if budget >= 2_000_000:
        score += 25
        reasons.append(f"Высокий бюджет: {budget:,} ₽".replace(",", " "))
    elif budget >= 800_000:
        score += 15
        reasons.append(f"Солидный бюджет: {budget:,} ₽".replace(",", " "))
    elif budget >= 300_000:
        score += 8
        reasons.append("Бюджет в рабочем диапазоне")
    elif budget > 0:
        score -= 5
        reasons.append("Бюджет ниже среднего по ателье")
    else:
        score -= 8
        reasons.append("Бюджет не указан")

    if _MANAGER_RE.search(lead.role or "") or _MANAGER_RE.search(blob):
        score += 12
        reasons.append("ЛПР / руководящая роль")

    if _LARGE_RE.search(lead.company_size or "") or _LARGE_RE.search(
        lead.business_info or "",
    ):
        score += 10
        reasons.append("Крупный клиент / флот")

    volume = _text(lead.task_volume, lead.need_volume).lower()
    if any(k in volume for k in ("мног", "серия", "парк", "несколько")):
        score += 8
        reasons.append("Большой объём задачи")

    if lead.phone or lead.email:
        score += 4
    else:
        score -= 15
        reasons.append("Нет контактов для связи")

    if lead.interested_product or lead.task_type:
        score += 4

    score = max(0, min(100, score))

    if score >= 70 or is_urgent:
        temperature: Temperature = "hot"
        temperature_label = "Горячий"
    elif score >= 45:
        temperature = "warm"
        temperature_label = "Тёплый"
    else:
        temperature = "cold"
        temperature_label = "Холодный"

    worth = score >= 45 or is_urgent
    if worth and temperature == "hot":
        worth_label = "Да — приоритетный лёд, брать в работу сразу"
    elif worth:
        worth_label = "Да — имеет смысл квалифицировать"
    else:
        worth_label = "Скорее нет — низкий приоритет в очереди"

    needs_pm = (
        is_urgent
        or budget >= 1_200_000
        or temperature == "hot"
        or bool(_MANAGER_RE.search(lead.role or ""))
        or bool(_LARGE_RE.search(lead.company_size or ""))
    )
    if needs_pm:
        reasons.append("Рекомендован персональный менеджер")

    dept, dept_label = _department(lead, budget)

    return LeadAnalysis(
        temperature=temperature,
        temperature_label=temperature_label,
        score=score,
        is_urgent=is_urgent,
        worth_time=worth,
        worth_time_label=worth_label,
        needs_personal_manager=needs_pm,
        department=dept,
        department_label=dept_label,
        reasons=reasons[:6],
    )


def score_leads(leads: list[Lead]) -> list[ScoredLead]:
    scored = [
        ScoredLead(**lead.model_dump(), analysis=analyze_lead(lead))
        for lead in leads
    ]
    scored.sort(
        key=lambda item: (
            not item.analysis.is_urgent,
            -item.analysis.score,
            item.created_at is None,
            -(item.created_at.timestamp() if item.created_at else 0),
        ),
    )
    return scored


def queue_stats(scored: list[ScoredLead]) -> LeadQueueStats:
    by_dept: dict[str, int] = {}
    total_score = 0
    for item in scored:
        total_score += item.analysis.score
        label = item.analysis.department_label
        by_dept[label] = by_dept.get(label, 0) + 1
    n = len(scored)
    return LeadQueueStats(
        total=n,
        hot=sum(1 for s in scored if s.analysis.temperature == "hot"),
        warm=sum(1 for s in scored if s.analysis.temperature == "warm"),
        cold=sum(1 for s in scored if s.analysis.temperature == "cold"),
        urgent=sum(1 for s in scored if s.analysis.is_urgent),
        with_manager=sum(
            1 for s in scored if s.analysis.needs_personal_manager
        ),
        avg_score=round(total_score / n, 1) if n else 0,
        by_department=by_dept,
    )
