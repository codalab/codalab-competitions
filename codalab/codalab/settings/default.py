from .base import DevBase
import os

__all__ = ['Dev']


class Dev(DevBase):
    # This setting seems to be getting overridden to none unless specified here.
    ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
