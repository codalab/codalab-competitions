#!/usr/bin/env python
# Run this with the python from the CodaLab virtual environment
# 
from django.core.management import setup_environ
from mysite import settings

setup_environ(settings)

from apps.web.models import Competition, CompetitionPhase, CompetitionParticipant, ParticipantStatus
from apps.web.models import CompetitionDataset, ExternalFile, ExternalFileType


