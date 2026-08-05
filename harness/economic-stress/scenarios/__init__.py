"""
Economic stress scenarios for InFlux protocol.
"""

from .whale_accumulation import WhaleAccumulationScenario
from .panic_selling import PanicSellingScenario
from .dead_network import DeadNetworkScenario
from .explosive_adoption import ExplosiveAdoptionScenario
from .slow_adoption import SlowAdoptionScenario
from .spam_attacks import SpamAttackScenario
from .validator_dropout import ValidatorDropoutScenario
from .exchange_outage import ExchangeOutageScenario

__all__ = [
    "WhaleAccumulationScenario",
    "PanicSellingScenario",
    "DeadNetworkScenario",
    "ExplosiveAdoptionScenario",
    "SlowAdoptionScenario",
    "SpamAttackScenario",
    "ValidatorDropoutScenario",
    "ExchangeOutageScenario",
]
