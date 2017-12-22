#!/usr/bin/env python

import topology_converter as tc


def test_all_letter_hostname():
    assert tc.check_hostname("leaf") is True


def test_all_digit_hostname():
    assert tc.check_hostname("0000") is True


def test_letter_digit_hostname():
    assert tc.check_hostname("leaf01") is True


def test_digit_letter_hostname():
    assert tc.check_hostname("01leaf") is True


def test_mid_dash_hostname():
    assert tc.check_hostname("leaf-01") is True


def test_start_dot_hostname():
    assert tc.check_hostname(".leaf") is False


def test_start_dash_hostname():
    assert tc.check_hostname("-leaf") is False


def test_start_underscore_hostname():
    assert tc.check_hostname("_leaf") is False


def test_embedded_dot_hostname():
    assert tc.check_hostname("lea.f") is False


def test_end_dot_hostname():
    assert tc.check_hostname("leaf.") is False


def test_end_dash_hostname():
    assert tc.check_hostname("leaf-") is False


def test_start_space_hostname():
    assert tc.check_hostname(" leaf") is False


def test_end_space_hostname():
    assert tc.check_hostname("leaf ") is False


def test_mid_space_hostname():
    assert tc.check_hostname("le af") is False


def test_blank_hostname():
    assert tc.check_hostname("   ") is False
