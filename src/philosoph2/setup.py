import logging
from threading import Lock
from enum import Enum


def set_partners(id, number_philosophers):

    right_partner = f"ph{id - 1}" 
    left_partner = f"ph{id + 1}" 

    if id == 1:
        right_partner = f"ph{number_philosophers}"

    elif id == number_philosophers: 
        left_partner = "ph1"

    logging.info("my right partner: %s", right_partner)
    #logging.info("my left partner: %s", left_partner)

    return right_partner, left_partner