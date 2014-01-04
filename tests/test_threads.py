# import pytest
# from django import db
# from django.db import transaction
# from concurrency.exceptions import RecordModifiedError
# from concurrency.utils import refetch
# from tests.models import TriggerConcurrentModel
# from tests.util import test_concurrently
#

#
# @pytest.mark.django_db(transaction=True)
# @pytest.mark.skipIf(db.connection.vendor == 'sqlite', "in-memory sqlite db can't be used between threads")
# def test_threads_1():
#     obj = TriggerConcurrentModel.objects.create()
#     transaction.commit()
#
#     @test_concurrently(25)
#     def run():
#         for i in range(5):
#             while True:
#                 x = refetch(obj)
#                 transaction.commit()
#                 x.count += 1
#                 try:
#                     x.save()
#                     transaction.commit()
#                 except RecordModifiedError:
#                     # retry
#                     pass
#                 else:
#                     break
#
#     run()
#     assert refetch(obj).count == 5 * 25
#

#
# from django import db
# from django.db import transaction
# class ThreadTests(TransactionTestCase):
#     @pytest.mark.skipIf(db.connection.vendor == 'sqlite',"in-memory sqlite db can't be used between threads")
#     def test_threads_1(self):
#         """
# Run 25 threads, each incrementing a shared counter 5 times.
# """
#
#         obj = TriggerConcurrentModel.objects.create()
#         transaction.commit()
#
#         @test_concurrently(25)
#         def run():
#             for i in range(5):
#                 while True:
#                     x = refetch(obj)
#                     transaction.commit()
#                     x.count += 1
#                     try:
#                         x.save()
#                         transaction.commit()
#                     except RecordModifiedError:
#                         # retry
#                         pass
#                     else:
#                         break
#         run()
#         assert refetch(obj).count== 5 * 25
#
#     @pytest.mark.skipIf(db.connection.vendor == 'sqlite',"in-memory sqlite db can't be used between threads")
#     def test_threads_2(self):
#         """
# Run 25 threads, each incrementing a shared counter 5 times.
# """
#
#         obj = TriggerConcurrentModel.objects.create()
#         transaction.commit()
#
#         @test_concurrently(25)
#         def run():
#             for i in range(5):
#                 x = refetch(obj)
#                 transaction.commit()
#                 x.count += 1
#                 try:
#                     x.save()
#                     transaction.commit()
#                 except RecordModifiedError:
#                     transaction.rollback()
#                     break
#         run()
#         obj = refetch(obj)
#         assert obj.count == obj.version-1
