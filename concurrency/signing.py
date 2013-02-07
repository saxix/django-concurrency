# -*- coding: utf-8 -*-
from django.core.signing import Signer, BadSignature
from django.utils.functional import memoize

_cache = {}


def get_signer(version=0):
    # version is here for future implementations
    return Signer()

get_signer = memoize(get_signer, _cache, 0)
