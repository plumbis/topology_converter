#!/usr/bin/env python

import topology_converter as tc


def test_valid_mac():
    assert tc.validate_mac("443839ff0000") is True


def test_invalid_2colon_mac():
    assert tc.validate_mac("44:38:39:ff:00:00") is False


def test_invalid_4colon_mac():
    assert tc.validate_mac("4438:39ff:0000") is False


def test_invalid_2dot_mac():
    assert tc.validate_mac("44.38.39.00ff.00.00") is False


def test_invalid_4dot_mac():
    assert tc.validate_mac("4438.39ff.0000") is False


def test_invalid_letter_mac():
    if not tc.validate_mac("443839zz0000"):
        assert True


def test_invalid_multicast_mac():
    assert tc.validate_mac("01005e000000") is False


def test_invalid_broadcast_mac():
    assert tc.validate_mac("ffffffffffff") is False


def test_invalid_network_mac():
    assert tc.validate_mac("000000000000") is False


def test_too_short_mac():
    assert tc.validate_mac("0000") is False


def test_too_long_mac():
    assert tc.validate_mac("00000000000000") is False


def test_not_hex_mac():
    assert tc.validate_mac("0000beefcake") is False
