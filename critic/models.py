from django.db import models

class CriticItem(models.Model):
    content = models.TextField()

class AboutItem(models.Model):
    content = models.TextField()

class ContactItem(models.Model):
    content = models.TextField()

class ArtPiece:
    img: str
    era1: str
    era1Prob: str
    era2: str
    era2Prob: str
    mood: str
    valueRatioDark: str
    valueRatioMed: str
    valueRatioLight: str
    colorDomRgb: str
    colorDomHex: str
    colorAvgRgb: str
    colorAvgHex: str
    result_era1: str
    result_era1: str
    result_mood: str
    result_dark: str
    result_med: str
    result_light: str
    result_dom: str
    result_avg: str