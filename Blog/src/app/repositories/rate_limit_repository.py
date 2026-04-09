from fastcrud import FastCRUD
from ..models.rate_limits import RateLimit
from ..schemas.rate_limit import RateLimitCreateInternal, RateLimitRead, RateLimitUpdate, RateLimitUpdateInternal, RateLimitDelete


CRUDRateLimit = FastCRUD[RateLimit, RateLimitCreateInternal, RateLimitRead, RateLimitUpdate, RateLimitUpdateInternal, RateLimitDelete]
crud_rate_limits = CRUDRateLimit(RateLimit)