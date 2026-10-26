import streamlit as st
from datetime import date, timedelta
from functools import lru_cache
import collections
import collections.abc
from fpdf import FPDF
import io

# Parche de compatibilidad para frozendict en Python 3.10+
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping

from experta import Fact, KnowledgeEngine, Rule, MATCH, NOT, AS, TEST

# ==============================================================================
# BASE DE CONOCIMIENTO
# ==============================================================================
CIUDADES_VALIDAS = ("Tokio", "Kioto", "Osaka", "Hiroshima", "Nara")

PERFILES_VALIDOS = (
    "Cultural", "Recreativa", "Gastronómica", "Natural",
    "Moderno", "Explorador", "Relajante", "Ninguno"
)

# Catálogo oficial completo (134 actividades)
CATALOGO_ACTIVIDADES = [
    # TOKIO
    dict(id="TOK_01", ciudad="Tokio", nombre="Visita al Templo Senso-ji en Asakusa", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_02", ciudad="Tokio", nombre="Cruce de Shibuya y mirador Shibuya Sky", costo_usd=22, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_03", ciudad="Tokio", nombre="Tour gastronómico de sushi en Tsukiji", costo_usd=85, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="TOK_04", ciudad="Tokio", nombre="Recorrido por el Museo TeamLab Planets", costo_usd=38, meses_validos=[1, 3, 4, 5, 6, 7, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="TOK_05", ciudad="Tokio", nombre="Compras y anime en Akihabara", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_06", ciudad="Tokio", nombre="Paseo por los jardines de Shinjuku Gyoen", costo_usd=3, meses_validos=[3, 4, 5, 9, 10, 11], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="TOK_07", ciudad="Tokio", nombre="Tour histórico en el Palacio Imperial", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_08", ciudad="Tokio", nombre="Experiencia de cruce y compras en Harajuku", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_09", ciudad="Tokio", nombre="Cena en callejón Omoide Yokocho", costo_usd=40, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=False),
    dict(id="TOK_10", ciudad="Tokio", nombre="Visita a la Torre de Tokio y mirador", costo_usd=20, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_11", ciudad="Tokio", nombre="Excursión cultural al Santuario Meiji", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_12", ciudad="Tokio", nombre="Recorrido por el mercado de pescado Toyosu", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="TOK_13", ciudad="Tokio", nombre="Subida al Monte Takao (senderismo)", costo_usd=10, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="alta", categoria="natural", accesibilidad=False),
    dict(id="TOK_14", ciudad="Tokio", nombre="Visita al Museo Nacional de Tokio en Ueno", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_15", ciudad="Tokio", nombre="Compras tecnológicas en tiendas de Ginza", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_16", ciudad="Tokio", nombre="Espectáculo de lucha de Sumo en Ryogoku", costo_usd=50, meses_validos=[1, 5, 9], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_17", ciudad="Tokio", nombre="Paseo nocturno en barco por la Bahía", costo_usd=60, meses_validos=[3, 4, 5, 6, 7, 8], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_18", ciudad="Tokio", nombre="Tour de Ramen en el Museo Shin-Yokohama", costo_usd=25, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="TOK_19", ciudad="Tokio", nombre="Visita al mirador del Ayuntamiento en Shinjuku", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_20", ciudad="Tokio", nombre="Paseo por el barrio histórico de Yanaka", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=False),
    dict(id="TOK_21", ciudad="Tokio", nombre="Compras de moda vintage en Shimokitazawa", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_22", ciudad="Tokio", nombre="Visita al parque de atracciones Tokyo Dome City", costo_usd=45, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_23", ciudad="Tokio", nombre="Taller de preparación de Soba tradicional", costo_usd=40, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="gastronómica", accesibilidad=True),
    dict(id="TOK_24", ciudad="Tokio", nombre="Visita al templo budista Zojo-ji", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="TOK_25", ciudad="Tokio", nombre="Exploración de la isla artificial Odaiba", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="recreativa", accesibilidad=True),
    dict(id="TOK_26", ciudad="Tokio", nombre="Recorrido nocturno por los bares de Golden Gai", costo_usd=35, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=False),
    dict(id="TOK_27", ciudad="Tokio", nombre="Visita al Museo de Arte Digital Mori Building", costo_usd=35, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=True),
    dict(id="TOK_28", ciudad="Tokio", nombre="Paseo en los botes del Parque Inokashira", costo_usd=8, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="baja", categoria="natural", accesibilidad=False),
    # KIOTO
    dict(id="KIO_01", ciudad="Kioto", nombre="Visita al Pabellón Dorado (Kinkaku-ji)", costo_usd=4, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_02", ciudad="Kioto", nombre="Recorrido por los mil toriis de Fushimi Inari", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="KIO_03", ciudad="Kioto", nombre="Paseo por el Bosque de Bambú de Arashiyama", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="KIO_04", ciudad="Kioto", nombre="Ceremonia del té tradicional en Gion", costo_usd=45, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_05", ciudad="Kioto", nombre="Visita al Templo Kiyomizu-dera", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="KIO_06", ciudad="Kioto", nombre="Tour gastronómico por el Mercado de Nishiki", costo_usd=50, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="KIO_07", ciudad="Kioto", nombre="Caminata por el Camino de Filosofía", costo_usd=0, meses_validos=[3, 4, 5, 9, 10, 11], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="KIO_08", ciudad="Kioto", nombre="Visita al Castillo de Nijo", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_09", ciudad="Kioto", nombre="Alquiler y paseo con Kimono tradicional", costo_usd=35, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_10", ciudad="Kioto", nombre="Avistamiento de Geishas en el distrito de Gion", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_11", ciudad="Kioto", nombre="Visita al templo Ryoan-ji y su jardín zen", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_12", ciudad="Kioto", nombre="Excursión al Templo Ginkaku-ji (Pabellón de Plata)", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_13", ciudad="Kioto", nombre="Senderismo en el Monte Hiei", costo_usd=15, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="alta", categoria="natural", accesibilidad=False),
    dict(id="KIO_14", ciudad="Kioto", nombre="Visita al santuario Heian y sus grandes jardines", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_15", ciudad="Kioto", nombre="Degustación de matcha y dulces tradicionales", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="KIO_16", ciudad="Kioto", nombre="Visita al templo Sanjusangen-do (1001 estatuas)", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_17", ciudad="Kioto", nombre="Crucero tradicional en barco por el río Hozu", costo_usd=30, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=False),
    dict(id="KIO_18", ciudad="Kioto", nombre="Recorrido por las calles históricas de Sannenzaka", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=False),
    dict(id="KIO_19", ciudad="Kioto", nombre="Visita al templo Tofuku-ji en temporada de otoño", costo_usd=7, meses_validos=[10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_20", ciudad="Kioto", nombre="Taller de cocina japonesa tradicional", costo_usd=60, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="gastronómica", accesibilidad=True),
    dict(id="KIO_21", ciudad="Kioto", nombre="Visita al templo Nanzen-ji y acueducto romano", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_22", ciudad="Kioto", nombre="Paseo nocturno iluminado en el templo Kodai-ji", costo_usd=5, meses_validos=[4, 5, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_23", ciudad="Kioto", nombre="Visita al Museo Internacional del Manga", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_24", ciudad="Kioto", nombre="Excursión al barrio histórico de Ohara", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="KIO_25", ciudad="Kioto", nombre="Tour en bicicleta por los templos del norte", costo_usd=20, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="media", categoria="recreativa", accesibilidad=False),
    dict(id="KIO_26", ciudad="Kioto", nombre="Visita al templo Daigo-ji", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="KIO_27", ciudad="Kioto", nombre="Compra de artesanías en la calle Gojozaka", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    # OSAKA
    dict(id="OSA_01", ciudad="Osaka", nombre="Visita panorámica al Castillo de Osaka", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="OSA_02", ciudad="Osaka", nombre="Recorrido gastronómico nocturno en Dotonbori", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="OSA_03", ciudad="Osaka", nombre="Visita al parque de atracciones Universal Studios Japan", costo_usd=75, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="alta", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_04", ciudad="Osaka", nombre="Subida a la Torre Umeda Sky Building", costo_usd=12, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_05", ciudad="Osaka", nombre="Degustación de Takoyaki en Shinsekai", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=False),
    dict(id="OSA_06", ciudad="Osaka", nombre="Compras y ambiente retro en Shinsekai", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=False),
    dict(id="OSA_07", ciudad="Osaka", nombre="Visita al acuario Kaiyukan de Osaka", costo_usd=20, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_08", ciudad="Osaka", nombre="Compras en el mercado Kuromon Ichiba", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="OSA_09", ciudad="Osaka", nombre="Visita al templo Shitenno-ji", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_10", ciudad="Osaka", nombre="Paseo comercial por Shinsaibashi-suji", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_11", ciudad="Osaka", nombre="Crucero por el río Dotonbori (Tombori River Cruise)", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_12", ciudad="Osaka", nombre="Visita al Museo de la Vivienda y la Vida de Osaka", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="OSA_13", ciudad="Osaka", nombre="Degustación de Okonomiyaki en el barrio de Namba", costo_usd=20, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="OSA_14", ciudad="Osaka", nombre="Paseo por el parque Nakanoshima", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="OSA_15", ciudad="Osaka", nombre="Visita al santuario Sumiyoshi Taisha", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="OSA_16", ciudad="Osaka", nombre="Visita al Museo de Bellas Artes Nakanoshima", costo_usd=12, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="OSA_17", ciudad="Osaka", nombre="Compras de electrónica en Den Den Town", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_18", ciudad="Osaka", nombre="Subida a la Noria de HEP FIVE", costo_usd=5, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_19", ciudad="Osaka", nombre="Tour de comida callejera en el barrio de Tsuruhashi", costo_usd=25, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=False),
    dict(id="OSA_20", ciudad="Osaka", nombre="Visita al observatorio Tsutenkaku", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_21", ciudad="Osaka", nombre="Paseo por el barrio creativo de Orange Street", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_22", ciudad="Osaka", nombre="Visita al Parque Memorial de la Exposición de 1970", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="OSA_23", ciudad="Osaka", nombre="Experiencia en un Onsen urbano en Spa World", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_24", ciudad="Osaka", nombre="Tour nocturno de bares en el callejón Hozenji Yokocho", costo_usd=40, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=False),
    dict(id="OSA_25", ciudad="Osaka", nombre="Visita al templo Hozen-ji", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="OSA_26", ciudad="Osaka", nombre="Tour fotográfico por la zona portuaria de Tempozan", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="OSA_27", ciudad="Osaka", nombre="Taller de fabricación de réplicas de comida en cera", costo_usd=30, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="recreativa", accesibilidad=True),
    # HIROSHIMA
    dict(id="HIR_01", ciudad="Hiroshima", nombre="Visita al Parque Memorial de la Paz", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_02", ciudad="Hiroshima", nombre="Recorrido por el Museo Memorial de la Paz", costo_usd=2, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_03", ciudad="Hiroshima", nombre="Visita a la Cúpula de la Bomba Atómica", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_04", ciudad="Hiroshima", nombre="Excursión en ferry a la Isla de Miyajima", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="HIR_05", ciudad="Hiroshima", nombre="Visita al Gran Torii flotante del Santuario Itsukushima", costo_usd=3, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_06", ciudad="Hiroshima", nombre="Senderismo o teleférico al Monte Misen en Miyajima", costo_usd=12, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="alta", categoria="natural", accesibilidad=False),
    dict(id="HIR_07", ciudad="Hiroshima", nombre="Degustación de Okonomiyaki estilo Hiroshima en Okonomimura", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="HIR_08", ciudad="Hiroshima", nombre="Visita al Castillo de Hiroshima y su jardín", costo_usd=3, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_09", ciudad="Hiroshima", nombre="Paseo por los jardines Shukkei-en", costo_usd=2, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="HIR_10", ciudad="Hiroshima", nombre="Crucero turístico por la bahía de Hiroshima", costo_usd=20, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="HIR_11", ciudad="Hiroshima", nombre="Visita al Museo de Arte de Hiroshima", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_12", ciudad="Hiroshima", nombre="Compras y recuerdos en la calle comercial Hondori", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="HIR_13", ciudad="Hiroshima", nombre="Paseo en tranvía histórico por la ciudad", costo_usd=2, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="HIR_14", ciudad="Hiroshima", nombre="Degustación de ostras locales en Miyajima", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="HIR_15", ciudad="Hiroshima", nombre="Visita al templo Daisho-in en Miyajima", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="HIR_16", ciudad="Hiroshima", nombre="Excursión en bicicleta por la Isla de Etajima", costo_usd=15, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="media", categoria="recreativa", accesibilidad=False),
    dict(id="HIR_17", ciudad="Hiroshima", nombre="Visita al Museo de Mazda (fábrica de autos)", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_18", ciudad="Hiroshima", nombre="Caminata nocturna por el Parque de la Paz iluminado", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_19", ciudad="Hiroshima", nombre="Visita al templo Mitaki-dera", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="cultural", accesibilidad=False),
    dict(id="HIR_20", ciudad="Hiroshima", nombre="Tour de historia local en el barrio antiguo de Kusatsu", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_21", ciudad="Hiroshima", nombre="Degustación de dulces Momiji Manju en Miyajima", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="HIR_22", ciudad="Hiroshima", nombre="Asistencia a partido de beisbol en Mazda Zoom-Zoom", costo_usd=25, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="HIR_23", ciudad="Hiroshima", nombre="Observación de la puesta de sol en la costa de Miyajima", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="HIR_24", ciudad="Hiroshima", nombre="Visita al Museo de Ciencias de la Ciudad de Hiroshima", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="HIR_25", ciudad="Hiroshima", nombre="Paseo por el puerto comercial Ujina", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="recreativa", accesibilidad=True),
    dict(id="HIR_26", ciudad="Hiroshima", nombre="Visita al Santuario Gokoku", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    # NARA
    dict(id="NAR_01", ciudad="Nara", nombre="Visita al Gran Buda en el Templo Todai-ji", costo_usd=6, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_02", ciudad="Nara", nombre="Interacción con ciervos sika en el Parque de Nara", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="NAR_03", ciudad="Nara", nombre="Visita al Santuario Kasuga Taisha y sus linternas", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_04", ciudad="Nara", nombre="Recorrido por el jardín Isuien", costo_usd=9, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="NAR_05", ciudad="Nara", nombre="Visita al Templo Kofuku-ji y su pagoda de cinco pisos", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_06", ciudad="Nara", nombre="Paseo por el distrito histórico de Naramachi", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_07", ciudad="Nara", nombre="Visita al Museo Nacional de Nara", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_08", ciudad="Nara", nombre="Senderismo al Monte Wakakusa", costo_usd=2, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="alta", categoria="natural", accesibilidad=False),
    dict(id="NAR_09", ciudad="Nara", nombre="Visita al Templo Horyu-ji (fuera de la ciudad principal)", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_10", ciudad="Nara", nombre="Degustación de sushi envuelto en hojas de Kaki (Kaki-no-ha)", costo_usd=12, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="NAR_11", ciudad="Nara", nombre="Visita al Templo Gangoji, declarado patrimonio", costo_usd=4, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_12", ciudad="Nara", nombre="Paseo en botes tradicionales en el estanque Sarusawa", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="NAR_13", ciudad="Nara", nombre="Visita al Palacio Heijo (sitio arqueológico imperial)", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_14", ciudad="Nara", nombre="Taller de elaboración de mochi tradicional en Nakatanidou", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="NAR_15", ciudad="Nara", nombre="Excursión al Templo Toshodai-ji", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_16", ciudad="Nara", nombre="Visita al Templo Yakushiji", costo_usd=8, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_17", ciudad="Nara", nombre="Compras de artesanías tradicionales de Nara en Naramachi", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_18", ciudad="Nara", nombre="Visita al Jardín Botánico Manyo", costo_usd=0, meses_validos=[3, 4, 5, 6, 7, 8, 9, 10, 11], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_19", ciudad="Nara", nombre="Caminata nocturna por los farolillos de Kasuga Taisha", costo_usd=0, meses_validos=[2, 8], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_20", ciudad="Nara", nombre="Visita al santuario Himuro (santuario del hielo)", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_21", ciudad="Nara", nombre="Alquiler de bicicleta para recorrer los templos periféricos", costo_usd=15, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="media", categoria="recreativa", accesibilidad=False),
    dict(id="NAR_22", ciudad="Nara", nombre="Degustación de cerveza artesanal local en Naramachi", costo_usd=10, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="gastronómica", accesibilidad=True),
    dict(id="NAR_23", ciudad="Nara", nombre="Visita al Museo de Artes y Oficios de Naramachi", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_24", ciudad="Nara", nombre="Observación de aves en el humedal de Yamato", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True),
    dict(id="NAR_25", ciudad="Nara", nombre="Visita al Templo Saidai-ji", costo_usd=5, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="cultural", accesibilidad=True),
    dict(id="NAR_26", ciudad="Nara", nombre="Paseo por el parque Himuro y sus alrededores boscosos", costo_usd=0, meses_validos=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], exigencia="baja", categoria="natural", accesibilidad=True)
]

# ==============================================================================
# VALIDACIONES DETERMINÍSTICAS INICIALES
# ==============================================================================
def validar_solicitud(ciudad, presupuesto, dias, personas, desde, hasta, movilidad, perfil):
    errores = []
    if ciudad not in CIUDADES_VALIDAS:
        errores.append(f"Ciudad '{ciudad}' no válida. Opciones permitidas: {CIUDADES_VALIDAS}.")
    if not isinstance(dias, int) or not (1 <= dias <= 15):
        errores.append("La duración máxima acordada es de 15 días.")
    if not isinstance(presupuesto, (int, float)) or presupuesto <= 0:
        errores.append("El presupuesto debe ser numérico y mayor a 0 USD.")
    if not isinstance(personas, int) or personas < 1:
        errores.append("El viaje requiere al menos 1 persona.")
    if not isinstance(desde, date) or not isinstance(hasta, date):
        errores.append("Las fechas ingresadas son inválidas.")
    elif hasta < desde:
        errores.append("El rango de fechas está invertido (Fin es anterior a Inicio).")
    elif (hasta - desde).days + 1 < dias:
        errores.append("La ventana de calendario es más pequeña que los días de estadía pedidos.")
    if perfil not in PERFILES_VALIDOS:
        errores.append(f"El perfil '{perfil}' no existe. Opciones: {PERFILES_VALIDOS}.")
    return errores

# ==============================================================================
# DECLARACIÓN DE HECHOS (FACTS)
# ==============================================================================
class Viaje(Fact): pass
class Actividad(Fact): pass
class ErrorValidacion(Fact): pass
class SolicitudValida(Fact): pass
class Descartar(Fact): pass
class Elegible(Fact): pass
class Preferencia(Fact): pass
class OpcionAlojamiento(Fact): pass
class InfiereDiasLibres(Fact): pass
class PlanGenerado(Fact): pass
class Conflicto(Fact): pass

# ==============================================================================
# MOTOR DE INFERENCIA EXPERTA (25 REGLAS EN 5 FASES)
# ==============================================================================
class SistemaViajesJapon(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.traza = []
        self.resultado = None
        self.actividades_elegibles = {}

    def log(self, regla, msg):
        self.traza.append(f"[{regla}] {msg}")

    # ---------------- FASE 0: Validaciones Duras (salience 100) ----------------
    @Rule(Viaje(ciudad=MATCH.c), TEST(lambda c: c not in CIUDADES_VALIDAS), salience=100)
    def r01_validar_ciudad(self, c):
        self.declare(ErrorValidacion(motivo=f"La ciudad '{c}' no está permitida."))

    @Rule(Viaje(dias=MATCH.d), TEST(lambda d: not isinstance(d, int) or d <= 0 or d > 15), salience=100)
    def r02_validar_duracion(self, d):
        self.declare(ErrorValidacion(motivo="La duración debe estar entre 1 y 15 días."))

    @Rule(Viaje(presupuesto=MATCH.p), TEST(lambda p: p <= 0), salience=100)
    def r03_validar_presupuesto(self, p):
        self.declare(ErrorValidacion(motivo="El presupuesto debe ser mayor a 0."))

    @Rule(Viaje(personas=MATCH.p), TEST(lambda p: not isinstance(p, int) or p < 1), salience=100)
    def r04_validar_personas(self, p):
        self.declare(ErrorValidacion(motivo="Mínimo 1 persona en el viaje."))

    @Rule(Viaje(perfil=MATCH.p), TEST(lambda p: p not in PERFILES_VALIDOS), salience=100)
    def r05_validar_perfil(self, p):
        self.declare(ErrorValidacion(motivo="El perfil seleccionado no es válido."))

    @Rule(ErrorValidacion(motivo=MATCH.m), salience=95)
    def r06_notificar_error(self, m):
        self.log("R06", f"Bloqueo inicial: {m}")
        self.resultado = {"estado": "ERROR", "motivo": m}
        self.halt()

    @Rule(Viaje(), NOT(ErrorValidacion()), salience=90)
    def r07_iniciar_inferencia(self):
        self.declare(SolicitudValida())

    # ---------------- FASE 1: Filtros de Depuración (salience 80) ----------------
    @Rule(SolicitudValida(), Viaje(ciudad=MATCH.cv), AS.act << Actividad(id=MATCH.id, ciudad=MATCH.ca, nombre=MATCH.n),
          TEST(lambda cv, ca: cv != ca), salience=80)
    def r08_filtro_ciudad(self, act, id, n):
        self.log("R08", f"Descarte [{id}]: {n} pertenece a otra ciudad.")
        self.declare(Descartar(id=id))
        self.retract(act)

    @Rule(SolicitudValida(), Viaje(desde=MATCH.d1, hasta=MATCH.d2), AS.act << Actividad(id=MATCH.id, meses_validos=MATCH.m, nombre=MATCH.n),
          salience=80)
    def r09_filtro_temporada(self, act, id, n, d1, d2, m):
        meses_rango = set(d.month for d in (d1 + timedelta(days=i) for i in range((d2 - d1).days + 1)))
        if not any(mes in m for mes in meses_rango):
            self.log("R09", f"Descarte [{id}]: {n} está fuera de temporada (fechas incompatibles).")
            self.declare(Descartar(id=id))
            self.retract(act)

    # R10: FILTRO DE ACCESIBILIDAD PURA
    @Rule(SolicitudValida(), Viaje(movilidad=True), 
          AS.act << Actividad(id=MATCH.id, nombre=MATCH.n, accesibilidad=MATCH.acc), 
          TEST(lambda acc: acc is False),
          salience=80)
    def r10_filtro_accesibilidad(self, act, id, n, acc):
        self.log("R10", f"Descarte [{id}]: {n} no cuenta con accesibilidad para movilidad reducida.")
        self.declare(Descartar(id=id))
        self.retract(act)

    @Rule(SolicitudValida(), Actividad(id=MATCH.id, nombre=MATCH.n, costo_usd=MATCH.c, meses_validos=MATCH.m, categoria=MATCH.cat), NOT(Descartar(id=MATCH.id)), salience=75)
    def r11_marcar_elegible(self, id, n, c, m, cat):
        self.declare(Elegible(id=id))
        self.actividades_elegibles[id] = {'id': id, 'nombre': n, 'costo_usd': c, 'meses_validos': m, 'categoria': cat}

    # ---------------- FASE 2: Preferencias por Perfil (salience 60) ----------------
    @Rule(Viaje(perfil=MATCH.p), Elegible(id=MATCH.id), Actividad(id=MATCH.id, categoria=MATCH.cat),
          TEST(lambda p, cat: p.lower() in ("cultural",) and cat.lower() in ("cultural",)), salience=60)
    def r12_perfil_cultural(self, id):
        self.declare(Preferencia(id_actividad=id, bono=10))

    @Rule(Viaje(perfil=MATCH.p), Elegible(id=MATCH.id), Actividad(id=MATCH.id, categoria=MATCH.cat),
          TEST(lambda p, cat: p.lower() in ("recreativa", "recreativo", "moderno") and cat.lower() in ("recreativa",)), salience=60)
    def r13_perfil_recreativa(self, id):
        self.declare(Preferencia(id_actividad=id, bono=10))

    @Rule(Viaje(perfil=MATCH.p), Elegible(id=MATCH.id), Actividad(id=MATCH.id, categoria=MATCH.cat),
          TEST(lambda p, cat: p.lower() in ("gastronómica", "gastronomica", "gastronómico", "gastronomico") and cat.lower() in ("gastronómica", "gastronomica")), salience=60)
    def r14_perfil_gastronomica(self, id):
        self.declare(Preferencia(id_actividad=id, bono=10))

    @Rule(Viaje(perfil=MATCH.p), Elegible(id=MATCH.id), Actividad(id=MATCH.id, categoria=MATCH.cat),
          TEST(lambda p, cat: p.lower() in ("natural", "explorador", "relajante") and cat.lower() in ("natural",)), salience=60)
    def r15_perfil_natural(self, id):
        self.declare(Preferencia(id_actividad=id, bono=10))

    # ---------------- FASE 3: Deducción de Opciones de Hospedaje Referencial (salience 50) ----------------
    @Rule(SolicitudValida(), Viaje(ciudad=MATCH.c, dias=MATCH.d, personas=MATCH.pers), salience=50)
    def r16_alojamiento_economico(self, c, d, pers):
        tarifa = 30
        total = tarifa * pers * d
        self.declare(OpcionAlojamiento(
            orden=1,
            nivel="Económico",
            detalle=f"• [Económico] Hostel / Cápsula en {c}: ~USD {total} ({pers} pers. x {d} días x USD {tarifa}/noche)"
        ))

    @Rule(SolicitudValida(), Viaje(ciudad=MATCH.c, dias=MATCH.d, personas=MATCH.pers), salience=50)
    def r17_alojamiento_estandar(self, c, d, pers):
        tarifa = 80
        total = tarifa * pers * d
        self.declare(OpcionAlojamiento(
            orden=2,
            nivel="Estándar",
            detalle=f"• [Estándar] Hotel 3* en {c}: ~USD {total} ({pers} pers. x {d} días x USD {tarifa}/noche)"
        ))

    @Rule(SolicitudValida(), Viaje(ciudad=MATCH.c, dias=MATCH.d, personas=MATCH.pers), salience=50)
    def r18_alojamiento_lujo(self, c, d, pers):
        tarifa = 200
        total = tarifa * pers * d
        self.declare(OpcionAlojamiento(
            orden=3,
            nivel="Lujo",
            detalle=f"• [Lujo] Ryokan Tradicional / Hotel 5* en {c}: ~USD {total} ({pers} pers. x {d} días x USD {tarifa}/noche)"
        ))

    # ---------------- FASE 4: Días Libres y Empaquetado (salience 40 a 35) ----------------
    @Rule(SolicitudValida(), Viaje(dias=MATCH.d), TEST(lambda d: d >= 5), salience=40)
    def r19_dias_libres_si(self):
        self.declare(InfiereDiasLibres(aplicar=True))

    @Rule(SolicitudValida(), Viaje(dias=MATCH.d), TEST(lambda d: d < 5), salience=40)
    def r20_dias_libres_no(self):
        self.declare(InfiereDiasLibres(aplicar=False))

    @Rule(SolicitudValida(), Viaje(dias=MATCH.d, personas=MATCH.p, desde=MATCH.d1, hasta=MATCH.d2), InfiereDiasLibres(aplicar=MATCH.libres),
          salience=35)
    def r21_ejecutar_empaquetado(self, d, p, libres, d1, d2):
        pref_dict = {f['id_actividad']: f['bono'] for f in self.facts.values() if isinstance(f, Preferencia)}
        lista = list(self.actividades_elegibles.values())
        lista.sort(key=lambda x: (pref_dict.get(x['id'], 0), -x['costo_usd']), reverse=True)

        cronograma, costo_total, idx = [], 0, 0
        for dia_num in range(1, d + 1):
            if libres and dia_num % 5 == 0:
                cronograma.append((dia_num, "Día Libre / Descanso recomendado", 0, 0))
                continue
                
            if idx < len(lista):
                act = lista[idx]
                idx += 1
                costo_unit = act['costo_usd']
                costo_grupal = costo_unit * p
                costo_total += costo_grupal
                cronograma.append((dia_num, act['nombre'], costo_unit, costo_grupal))
            else:
                self.declare(PlanGenerado(valido=False))
                return
                
        opciones_aloj = sorted([f for f in self.facts.values() if isinstance(f, OpcionAlojamiento)], key=lambda x: x['orden'])
        aloj_detalles = [f['detalle'] for f in opciones_aloj]
        
        self.plan_final = {'costo': costo_total, 'itinerario': cronograma, 'alojamientos': aloj_detalles}
        self.declare(PlanGenerado(valido=True, costo=costo_total))

    # ---------------- FASE 5: Viabilidad y Relajación (salience 20 a 10) ----------------
    @Rule(PlanGenerado(valido=True, costo=MATCH.c), Viaje(presupuesto=MATCH.p), TEST(lambda c, p: c <= p), salience=20)
    def r22_resolucion_aprobada(self):
        self.resultado = {"estado": "APROBADO", **self.plan_final}

    @Rule(PlanGenerado(valido=True, costo=MATCH.c), Viaje(presupuesto=MATCH.p), TEST(lambda c, p: c > p), salience=20)
    def r23_resolucion_conflicto(self):
        self.declare(Conflicto())

    @Rule(PlanGenerado(valido=False), salience=20)
    def r24_resolucion_sin_actividades(self):
        self.resultado = {"estado": "SIN_ACTIVIDADES", "motivo": "El catálogo se agotó antes de poder cubrir todos los días solicitados. Pruebe otro destino o reduzca la estadía."}

    @Rule(Conflicto(), Viaje(dias=MATCH.d, presupuesto=MATCH.p, personas=MATCH.pers), salience=10)
    def r25_sugerir_reduccion_dias(self, d, p, pers):
        pref_dict = {f['id_actividad']: f['bono'] for f in self.facts.values() if isinstance(f, Preferencia)}
        lista = list(self.actividades_elegibles.values())
        lista.sort(key=lambda x: (pref_dict.get(x['id'], 0), -x['costo_usd']), reverse=True)

        dias_propuestos = 0
        nuevo_costo = 0

        for dias_candidatos in range(d - 1, 0, -1):
            costo_sim = 0
            idx = 0
            libres_sim = (dias_candidatos >= 5)
            posible = True
            for dia_num in range(1, dias_candidatos + 1):
                if libres_sim and dia_num % 5 == 0:
                    continue
                if idx < len(lista):
                    costo_sim += lista[idx]['costo_usd'] * pers
                    idx += 1
                else:
                    posible = False
                    break
            if posible and costo_sim <= p:
                dias_propuestos = dias_candidatos
                nuevo_costo = costo_sim
                break

        if dias_propuestos > 0:
            self.resultado = {
                "estado": "REDUCIR_DIAS",
                "dias_propuestos": dias_propuestos,
                "nuevo_costo": nuevo_costo,
                "costo_original": self.plan_final['costo']
            }
        else:
            self.resultado = {
                "estado": "SIN_SOLUCION",
                "motivo": "El presupuesto ingresado es tan bajo que no cubre ni un solo día del viaje con las preferencias indicadas."
            }

# FUNCION PARA EXPORTACIÓN PDF

def generar_pdf(resultado, ciudad, personas):
    pdf = FPDF()
    pdf.add_page()
    
    # Título principal
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, text=f"Itinerario Experto: {ciudad}", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # --- NUEVO: Fecha de generación ---
    pdf.set_font("Arial", 'I', 10) # Letra en cursiva (Italic) y más chica
    fecha_actual = date.today().strftime("%d/%m/%Y")
    pdf.cell(190, 8, text=f"Generado el: {fecha_actual}", align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Resumen de Costos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 10, text=f"Costo Total Actividades: USD {resultado['costo']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Alojamientos
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, text="Estimacion de Hospedaje", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", size=11)
    for aloj in resultado['alojamientos']:
        texto_aloj = aloj.replace('•', '-').replace('~', '')
        pdf.multi_cell(190, 8, text=texto_aloj, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Itinerario
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, text="Cronograma Diario Propuesto", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", size=11)
    for d in resultado['itinerario']:
        dia_num, nombre, costo_unit, costo_tot = d[0], d[1], d[2], d[3]
        if "Descanso" in nombre:
            texto = f"Dia {dia_num}: {nombre}"
        else:
            texto = f"Dia {dia_num}: {nombre} ({personas} pers. x USD {costo_unit} = USD {costo_tot})"
        pdf.multi_cell(190, 8, text=texto, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
# ==============================================================================
# INTERFAZ STREAMLIT
# ==============================================================================
st.set_page_config(page_title="Experto en Viajes a Japón", page_icon="🏯", layout="centered")

st.title("🏯 Planificador Experto - Viajes a Japón")
st.markdown("Este sistema experto deductivo genera itinerarios viables basados en inferencia lógica y reglas condicionales (Forward Chaining).")

# Funciones de callback para sincronizar Fechas y Días en tiempo real
def actualizar_por_fechas():
    if st.session_state.fecha_inicio and st.session_state.fecha_fin:
        if st.session_state.fecha_fin >= st.session_state.fecha_inicio:
            st.session_state.dias = (st.session_state.fecha_fin - st.session_state.fecha_inicio).days + 1
        else:
            st.session_state.dias = None

def actualizar_por_dias():
    if st.session_state.fecha_inicio and st.session_state.dias:
        st.session_state.fecha_fin = st.session_state.fecha_inicio + timedelta(days=int(st.session_state.dias) - 1)

# Iniciar la memoria de Streamlit para que vengan limpios
if 'fecha_inicio' not in st.session_state: st.session_state.fecha_inicio = None
if 'fecha_fin' not in st.session_state: st.session_state.fecha_fin = None
if 'dias' not in st.session_state: st.session_state.dias = None

col1, col2 = st.columns(2)

with col1:
    # Usamos index=None y value=None para que aparezcan vacíos por defecto
    ciudad = st.selectbox("📍 Ciudad Destino", CIUDADES_VALIDAS, index=None, placeholder="Seleccioná una ciudad")
    presupuesto = st.number_input("💰 Presupuesto para actividades (USD)", min_value=1, value=None, step=50, placeholder="Ej: 200")
    personas = st.number_input("👥 Cantidad de personas", min_value=1, value=None, step=1, placeholder="Ej: 2")
    perfil = st.selectbox("🎭 Perfil de Viaje (Opcional)", PERFILES_VALIDOS, index=None, placeholder="Sin especificar")
    
with col2:
    # Usamos on_change para disparar el cálculo automático apenas el usuario toca algo
    st.date_input("📅 Fecha de Inicio", value=None, key="fecha_inicio", on_change=actualizar_por_dias)
    st.date_input("📅 Fecha de Fin", value=None, key="fecha_fin", on_change=actualizar_por_fechas)
    st.number_input("🗓️ Cantidad de Días de Estadía", min_value=1, max_value=15, value=None, step=1, key="dias", on_change=actualizar_por_dias)
    
    movilidad = st.checkbox("♿ Requiere Accesibilidad (Movilidad Reducida)")
    
# Usamos un botón nativo en vez de form_submit_button
submit = st.button("🔍 Ejecutar Inferencia Experta")

if submit:
    # Rescatamos los valores del estado (memoria) ya que están enlazados dinámicamente
    fecha_in = st.session_state.fecha_inicio
    fecha_out = st.session_state.fecha_fin
    dias_est = st.session_state.dias

    # 1. Validación de campos obligatorios vacíos
    faltantes = []
    if not ciudad: faltantes.append("Ciudad Destino")
    if not presupuesto: faltantes.append("Presupuesto")
    if not personas: faltantes.append("Cantidad de personas")
    if not fecha_in: faltantes.append("Fecha de Inicio")
    if not fecha_out: faltantes.append("Fecha de Fin")
    if not dias_est: faltantes.append("Cantidad de Días")

    if faltantes:
        st.error("❌ Faltan completar los siguientes campos obligatorios:")
        for f in faltantes:
            st.warning(f"• {f}")
            
    elif fecha_out < fecha_in:
        st.error("❌ Incoherencia: La Fecha de Fin no puede ser anterior a la de Inicio.")
        
    else:
        # Si no seleccionó perfil, mandamos "Ninguno" para no trabar el motor
        perfil_final = perfil if perfil else "Ninguno"
        
        errores = validar_solicitud(ciudad, presupuesto, dias_est, personas, fecha_in, fecha_out, movilidad, perfil_final)
        
        if errores:
            st.error("❌ ERROR EN PARÁMETROS (Inferencia Bloqueada):")
            for e in errores:
                st.warning(f"• {e}")
        if errores:
            st.error("❌ ERROR EN PARÁMETROS (Inferencia Bloqueada):")
            for e in errores:
                st.warning(f"• {e}")
        else:
            # 2. Correr motor Rete
            motor = SistemaViajesJapon()
            motor.reset()
            
            for act in CATALOGO_ACTIVIDADES:
                motor.declare(Actividad(**act))
                
            motor.declare(Viaje(ciudad=ciudad, presupuesto=presupuesto, dias=dias_est, personas=personas,
                                desde=fecha_in, hasta=fecha_out, movilidad=movilidad, perfil=perfil_final))
            motor.run()
            
            # Guardar resultados en la memoria de la sesión
            st.session_state['resultado_experto'] = motor.resultado
            st.session_state['traza'] = motor.traza
            st.session_state['datos_viaje'] = {'ciudad': ciudad, 'personas': personas, 'presupuesto': presupuesto}

# Renderizar UI independiente del botón submit
if 'resultado_experto' in st.session_state:
    res = st.session_state['resultado_experto']
    datos = st.session_state['datos_viaje']
    
    if res['estado'] == 'APROBADO':
        st.success("✅ ¡ITINERARIO APROBADO Y GENERADO!")
        saldo = datos['presupuesto'] - res['costo']
        
        st.info(f"**🎢 Costo Total Actividades:** USD {res['costo']} (Saldo restante: USD {saldo})")
        
        st.subheader(f"🏨 Estimación Referencial de Hospedaje en {datos['ciudad'].upper()}")
        for linea in res['alojamientos']:
            st.write(linea)
        
        st.subheader("🗺️ Cronograma Diario Propuesto")
        for d in res['itinerario']:
            dia_num, nombre, costo_unit, costo_tot = d[0], d[1], d[2], d[3]
            if "Descanso" in nombre:
                st.markdown(f"**🌿 Día {dia_num}:** {nombre}")
            else:
                st.markdown(f"**📍 Día {dia_num}:** {nombre} _({datos['personas']} pers. x USD {costo_unit} = USD {costo_tot})_")
                
        with st.expander("Ver Traza de Decisiones del Motor Experto"):
            for t in st.session_state['traza']:
                st.text(t)
                
        # Generar y mostrar botón de PDF
        pdf_bytes = generar_pdf(res, datos['ciudad'], datos['personas'])
        st.download_button(
            label="📄 Descargar Itinerario en PDF",
            data=pdf_bytes,
            file_name=f"Itinerario_{datos['ciudad']}.pdf",
            mime="application/pdf"
        )

    elif res['estado'] == 'REDUCIR_DIAS':
        st.warning(f"⚠️ CONFLICTO PRESUPUESTARIO: El costo mínimo evaluado (USD {res['costo_original']}) excede tu presupuesto.")
        st.success(f"👉 **RELAJACIÓN APLICADA:** Se sugiere reducir la estadía a **{res['dias_propuestos']} días** para que el costo baje a **USD {res['nuevo_costo']}**.")
        
    else:
        st.error(f"❌ BLOQUEO DEL SISTEMA: {res['motivo']}")
