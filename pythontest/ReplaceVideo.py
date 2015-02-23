#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to upload a Video to the Xibo CMS and replace
# an old copy of it in a region

# Imports
import os
from xml.dom import minidom
import XiboAPI

api = XiboAPI.XiboAPI()
