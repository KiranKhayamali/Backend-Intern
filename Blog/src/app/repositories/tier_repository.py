from fastcrud import FastCRUD
from ..models.tiers import Tier
from ..schemas.tier import TierCreateInternal, TierRead, TierUpdate, TierUpdateInternal, TierDelete


CRUDTier = FastCRUD[Tier, TierCreateInternal, TierRead, TierUpdate, TierUpdateInternal, TierDelete]
crud_tiers = CRUDTier(Tier)

