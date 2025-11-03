import pytest

from varasto import Varasto


def test_tilavuus_nollataan_jos_negatiivinen():
    v = Varasto(-5)
    assert v.tilavuus == 0.0


def test_alkusaldo_negatiivinen_nollataan():
    v = Varasto(10, -3)
    assert v.saldo == 0.0


def test_alkusaldo_suurempi_kuin_tilavuus_tayteen():
    v = Varasto(10, 15)
    assert v.saldo == 10


def test_lisaa_varastoon_negatiivinen_ei_muuta_saldoa():
    v = Varasto(10, 5)
    v.lisaa_varastoon(-4)
    assert v.saldo == 5


def test_lisaa_varastoon_yli_tilavuuden_tayttaa():
    v = Varasto(10, 8)
    v.lisaa_varastoon(10)
    assert v.saldo == 10


def test_ota_varastosta_negatiivinen_palauttaa_nolla_ei_muuta():
    v = Varasto(10, 5)
    saatu = v.ota_varastosta(-2)
    assert saatu == 0.0
    assert v.saldo == 5


def test_ota_varastosta_enemman_kuin_saldo_palauttaa_kaiken_ja_nollaa():
    v = Varasto(10, 4)
    saatu = v.ota_varastosta(10)
    assert saatu == 4
    assert v.saldo == 0.0


def test___str___sisaltaa_saldo_ja_mahdollisen_tilan():
    v = Varasto(10, 3)
    assert str(v) == "saldo = 3, vielä tilaa 7"
