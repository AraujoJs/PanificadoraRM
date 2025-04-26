# coding: UTF-8
"""
Script: Panificadora-RM/map
Création: jojo, le 26/04/2025
"""
import flask


# Fonctions
def site_map(url_map):
    """Plan d'un site sous forme d'une liste 2D contenant la description de
    chaque route de forme ``{'route': "/", 'endpoint': "index", 'methods': "GET, POST", 'url': "/" (si possible)}``.
    """

    def has_no_empty_params(rule):
        """Détecte la présence de paramètres sans valeur par défaut"""
        defaults = rule.defaults if rule.defaults is not None else ()
        arguments = rule.arguments if rule.arguments is not None else ()
        return len(defaults) >= len(arguments)

    links = []
    for rule in url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if rule.endpoint == 'static':
            continue
        methods = [r for r in rule.methods if r not in ["OPTIONS", "HEAD"]]
        link = {'route': rule.rule, 'endpoint': rule.endpoint, 'methods': ", ".join(methods), 'url': None}
        if "GET" in rule.methods and has_no_empty_params(rule):
            link['url'] = flask.url_for(rule.endpoint, **(rule.defaults or {}))
        links.append(link)
    return links
