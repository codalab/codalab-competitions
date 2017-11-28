from django import template

register = template.Library()

@register.filter
def has_applied(team, user):
    return team.has_applied(user)

@register.filter
def is_member(team, user):
    return team.is_member(user)

@register.filter
def is_admin(team, user):
    return team.creator==user

