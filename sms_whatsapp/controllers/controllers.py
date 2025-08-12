# -*- coding: utf-8 -*-
# from odoo import http


# class SmsEvolution(http.Controller):
#     @http.route('/sms_evolution/sms_evolution', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sms_evolution/sms_evolution/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sms_evolution.listing', {
#             'root': '/sms_evolution/sms_evolution',
#             'objects': http.request.env['sms_evolution.sms_evolution'].search([]),
#         })

#     @http.route('/sms_evolution/sms_evolution/objects/<model("sms_evolution.sms_evolution"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sms_evolution.object', {
#             'object': obj
#         })

