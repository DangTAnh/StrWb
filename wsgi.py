import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.db import resequence_product_ids

app = create_app()

# Compact product ids on startup so auto SKUs (#1, #2, ...) stay contiguous
# after deletions. No-op when ids are already gapless.
with app.app_context():
    n = resequence_product_ids()
    if n:
        print(f'[resequence] compacted product ids: {n} products re-indexed')
