from __future__ import annotations

import argparse
import asyncio
from datetime import date
import json

from .service import CollectionService


async def main():
    parser = argparse.ArgumentParser(description="AEROVA compliant live fare collector")
    parser.add_argument("--source", default="INDIGO_PUBLIC_ROUTE")
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--adults", type=int, default=1)
    parser.add_argument("--cabin", default="Economy")
    args = parser.parse_args()

    service = CollectionService()
    rows = await service.collect(
        args.source,
        args.origin,
        args.destination,
        date.fromisoformat(args.date),
        args.adults,
        args.cabin,
    )
    print(json.dumps([r.to_dict() for r in rows], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
