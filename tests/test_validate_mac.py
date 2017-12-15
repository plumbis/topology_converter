#!/usr/bin/env python
import topology_converter as tc


def valid_mac():
    assert tc.validate_mac("443839ff0000") is True


def invalid_2colon_mac():
    assert tc.validate_mac("44:38:39:ff:00:00") is False


def invalid_4colon_mac():
    assert tc.validate_mac("4438:39ff:0000") is False


def invalid_2dot_mac():
    assert tc.validate_mac("44.38.39.00ff.00.00") is False


def invalid_4dot_mac():
    assert tc.validate_mac("4438.39ff.0000") is False


def invalid_letter_mac():
    assert tc.valdiate_mac("443839zz0000") is False


def invalid_multicast_mac():
    assert tc.valdiate_mac("01005e000000") is False


def invalid_broadcast_mac():
    assert tc.validate_mac("ffffffffffff") is False


def invalid_network_mac():
    assert tc.validate_mac("000000000000") is False
