from django.db import models


class TestCaseQuerySet(models.QuerySet):

    def performance_testcase(self):
        return self.filter(testcase_type='performance',)

    def smoke_testcase(self):
        return self.filter(testcase_type='smoke')

    def soak_testcase(self):
        return self.filter(testcase_type='soak')


class TestCaseManager(models.Manager):

    def get_queryset(self):
        return TestCaseQuerySet(self.model, using=self._db)

    def performance_testcase(self):
        return self.get_queryset().performance_testcase()

    def smoke_testcase(self):
        return self.get_queryset().smoke_testcase()

    def soak_testcase(self):
        return self.get_queryset().soak_testcase()