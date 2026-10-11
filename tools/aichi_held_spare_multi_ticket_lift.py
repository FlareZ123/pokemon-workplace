"""Exact Ticket 1..4 multiplicity sensitivity for Aichi paid-spare G&H route.

Count accepted openings with natural Jirachi and G&H, held one TM and
Jet, searchable spare copies and Artazon, no Ticket already held,
and k=0..q Tickets searchable after six Prizes. Compute optimistic
direct first unused Stellar Wish at-least-one-Ticket lift when paid G&H
searches spare Tool/Energy and thins deck by exactly two non-Tickets.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from tools.aichi_held_spare_gnh_opportunity import exact as source_event


def c(n: int,k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


def ticket_at_least_one(deck_size: int, copies: int, inspect: int) -> Fraction:
    if not (0 <= copies <= deck_size and 0 <= inspect <= deck_size):
        raise ValueError("Invalid target distribution")
    return Fraction(
        c(deck_size,inspect)-c(deck_size-copies,inspect),
        c(deck_size,inspect),
    )


@dataclass(frozen=True)
class Summary:
    tickets: int
    available_ticket_masses: tuple[tuple[int, Fraction], ...]
    no_held_ticket_and_sources_mass: Fraction
    optimistic_accepted_access_gain: Fraction


def exact(
    tickets: int, n: int = 60, opener: int = 7, prizes: int = 6,
    basics: int = 14, gnh: int = 4, artazon: int = 2,
    stellar_cards: int = 5,
) -> Summary:
    if not 1 <= tickets <= 4:
        raise ValueError("Ticket tech copy count must be 1..4")
    base = source_event(n,opener,prizes,basics,gnh,artazon)
    filler = n-1-gnh-4-artazon-tickets
    if basics > filler+1:
        raise ValueError("Not enough non-target residual Basic cards")
    unseen = n-1-opener
    deck_before_search = unseen-prizes
    if not 1 <= stellar_cards <= deck_before_search-3:
        raise ValueError("Too few cards for postsearch observation")

    masses: list[tuple[int,Fraction]] = []
    for searchable_tickets in range(tickets+1):
        ticket_prizes = tickets-searchable_tickets
        world_mass = Fraction(0)
        for held_gnh in range(1,gnh+1):
            for held_artazon in range(artazon):
                other_visible = opener-held_gnh-2-held_artazon
                observed_ways = (
                    c(gnh,held_gnh)*c(2,1)**2*c(artazon,held_artazon)*
                    c(filler,other_visible)
                )
                art_left = artazon-held_artazon
                other_unknown = unseen-2-art_left-tickets
                prize_ways = sum(
                    c(art_left,j)*c(tickets,ticket_prizes)*
                    c(other_unknown,prizes-j-ticket_prizes)
                    for j in range(art_left)
                )
                world_mass += (
                    Fraction(opener,n) *
                    Fraction(observed_ways,c(n-1,opener)) *
                    Fraction(prize_ways,c(unseen,prizes)) /
                    base.accepted_probability
                )
        masses.append((searchable_tickets,world_mass))

    gain = sum((
        mass*(
            ticket_at_least_one(deck_before_search-3,k,stellar_cards)
            -ticket_at_least_one(deck_before_search-1,k,stellar_cards)
        )
        for k,mass in masses
    ),Fraction(0))
    found_mass = sum((mass for _,mass in masses),Fraction(0))
    assert found_mass <= base.probability
    return Summary(tickets,tuple(masses),found_mass,gain)
