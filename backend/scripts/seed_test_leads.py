"""Insert 10 demo leads (4 urgent). Run inside backend container."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.database import close_pool, init_pool
from models.lead import Lead, LeadCRUD

SAMPLES: list[Lead] = [
    # --- 4 urgent / hot ---
    Lead(
        first_name="Артём",
        last_name="Соколов",
        email="a.sokolov@premium-fleet.ru",
        phone="+7 916 100-10-01",
        business_info="Парк Mercedes S-Class, 12 авто",
        niche="Корпоративный флот",
        company_size="крупная компания 500+",
        task_volume="серия из 12 машин",
        need_volume="много",
        role="директор по закупкам",
        budget="2800000",
        contact_method="телефон",
        convenient_time="сегодня до 18:00",
        comments="Срочно к презентации инвесторов на этой неделе",
        deadline="срочно, до пятницы",
        task_type="Покраска кузова",
        interested_product="Покраска кузова",
    ),
    Lead(
        first_name="Елена",
        last_name="Волкова",
        email="elena@volkova.vip",
        phone="+7 903 222-33-44",
        business_info="Porsche 911 Turbo S 2024",
        niche="Частный премиум",
        company_size="частный клиент",
        task_volume="1 авто, полный комплекс",
        role="владелец",
        budget="3500000",
        contact_method="telegram",
        comments="Горит срок — нужна акустика Bose ASAP",
        deadline="завтра",
        task_type="Акустика Bose",
        interested_product="Акустика Bose",
    ),
    Lead(
        first_name="Игорь",
        last_name="Макаров",
        phone="+7 926 555-01-02",
        email="makarov@holding.example",
        business_info="Range Rover Autobiography",
        niche="Холдинг / топ-менеджмент",
        company_size="холдинг 1000+",
        task_volume="несколько авто руководства",
        role="CEO",
        budget="1900000",
        contact_method="whatsapp",
        comments="Как можно быстрее, важный клиент холдинга",
        deadline="срочно",
        task_type="Аэрография",
        interested_product="Аэрография",
    ),
    Lead(
        first_name="Мария",
        last_name="Кузнецова",
        phone="+7 999 111-22-33",
        email="m.kuz@dealer.group",
        business_info="BMW X7, демо-парк дилера",
        niche="Автодилер",
        company_size="крупный дилерский центр",
        task_volume="парк 8 машин",
        role="руководитель отдела",
        budget="2200000",
        contact_method="телефон",
        comments="Срочная подготовка шоурума",
        deadline="эта неделя",
        task_type="Покраска кузова",
        interested_product="Покраска кузова",
    ),
    # --- 6 warmer / colder ---
    Lead(
        first_name="Дмитрий",
        last_name="Орлов",
        phone="+7 915 444-55-66",
        email="orlov@mail.example",
        business_info="Audi Q7 2021",
        niche="Частный",
        company_size="малый бизнес",
        task_volume="одна машина",
        role="сотрудник",
        budget="650000",
        contact_method="email",
        comments="Интересует Bose, сроки гибкие",
        deadline="в течение месяца",
        interested_product="Акустика Bose",
    ),
    Lead(
        first_name="Ольга",
        last_name="Смирнова",
        phone="+7 926 777-88-99",
        business_info="Lexus LX",
        niche="Частный",
        company_size="семья",
        role="менеджер",
        budget="1100000",
        contact_method="телефон",
        convenient_time="будни после 19:00",
        deadline="к лету",
        interested_product="Аэрография",
        comments="Хотим авторский рисунок",
    ),
    Lead(
        first_name="Павел",
        last_name="Никитин",
        email="p.nikitin@example.com",
        phone="+7 903 321-00-11",
        business_info="Toyota Camry",
        niche="Такси / парк",
        company_size="10–50",
        task_volume="2–3 авто",
        role="сотрудник",
        budget="280000",
        contact_method="whatsapp",
        deadline="не срочно",
        interested_product="Покраска кузова",
        comments="Смотрим варианты, бюджет ограничен",
    ),
    Lead(
        first_name="Сергей",
        last_name="Белов",
        phone="+7 916 888-00-22",
        business_info="Mercedes GLE",
        niche="Частный",
        company_size="ИП",
        role="владелец",
        budget="900000",
        contact_method="telegram",
        deadline="2–3 месяца",
        interested_product="Акустика Bose",
    ),
    Lead(
        first_name="Анна",
        last_name="Фёдорова",
        email="anna.f@example.com",
        business_info="Kia Sportage",
        niche="Частный",
        company_size="частное лицо",
        role="сотрудник",
        budget="150000",
        contact_method="email",
        comments="Просто узнать цены",
        deadline="когда-нибудь",
        interested_product="Аэрография",
    ),
    Lead(
        first_name="Кирилл",
        last_name="Громов",
        phone="+7 925 101-20-30",
        email="gromov@studio.example",
        business_info="Bentley Continental GT",
        niche="Медиа / шоу",
        company_size="агентство 50–100",
        task_volume="1 авто под съёмку",
        role="продюсер",
        budget="750000",
        contact_method="телефон",
        convenient_time="днём",
        deadline="через 3 недели",
        interested_product="Покраска кузова",
        comments="Нужен яркий цвет под клип",
    ),
]


async def main() -> None:
    await init_pool()
    await LeadCRUD.ensure_table()
    created = 0
    for sample in SAMPLES:
        await LeadCRUD.create(sample)
        created += 1
    await close_pool()
    print(f"seeded {created} leads")


if __name__ == "__main__":
    asyncio.run(main())
