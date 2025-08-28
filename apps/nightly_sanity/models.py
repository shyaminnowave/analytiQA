# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApkFiles(models.Model):
    filename = models.CharField(max_length=255)
    natco = models.CharField(max_length=50)
    file_path = models.CharField(max_length=255)
    upload_date = models.DateTimeField()
    release = models.ForeignKey('Releases', models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    @property
    def get_build_version(self):
        return self.file_path.split('-')[2]

    class Meta:
        managed = False
        db_table = 'apk_files'


class ApkInstallations(models.Model):
    apk = models.ForeignKey(ApkFiles, models.DO_NOTHING, blank=True, null=True)
    stb_node = models.ForeignKey('StbNodes', models.DO_NOTHING, blank=True, null=True)
    start_time = models.DateTimeField()
    result = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    failure_reason = models.TextField(blank=True, null=True)
    job_uid = models.CharField(max_length=255, blank=True, null=True)
    result_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'apk_installations'


class Releases(models.Model):
    major_release = models.CharField(max_length=50)
    sub_release = models.CharField(max_length=50)
    box_release_info = models.CharField(max_length=100)
    release_date = models.DateField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'releases'


class StbNodes(models.Model):
    node_id = models.CharField(max_length=50)
    friendly_name = models.CharField(max_length=100)
    natco = models.CharField(max_length=50)
    release = models.ForeignKey(Releases, models.DO_NOTHING, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stb_nodes'


class TestCases(models.Model):
    testcase_name = models.CharField(max_length=100)
    functionality = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    testcase_number = models.CharField(max_length=100)
    test_path = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_cases'


class TestExecutions(models.Model):
    stb_node = models.ForeignKey(StbNodes, models.DO_NOTHING, blank=True, null=True)
    test = models.ForeignKey(TestCases, models.DO_NOTHING, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_iterations = models.IntegerField(blank=True, null=True)
    passed_iterations = models.IntegerField(blank=True, null=True)
    failed_iterations = models.IntegerField(blank=True, null=True)
    error_iterations = models.IntegerField(blank=True, null=True)
    overall_status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    natco = models.CharField(max_length=50, blank=True, null=True)
    release_id = models.IntegerField(blank=True, null=True)
    apk_installation = models.ForeignKey(ApkInstallations, models.DO_NOTHING, blank=True, null=True)
    testcase_number = models.IntegerField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'test_executions'
        unique_together = (('start_time', 'end_time'),)
    
    @property
    def get_release(self):
        release = Releases.objects.using('sanity').get(id=self.release_id)
        return release.box_release_info
    
    @property
    def get_testcase(self):
        testcase = TestCases.objects.using('sanity').get(id=self.testcase_number)
        return testcase.functionality
    
    @property
    def get_testcase_name(self):
        testcase = TestCases.objects.using('sanity').get(id=self.testcase_number)
        return testcase.testcase_name

class TestIterations(models.Model):
    execution = models.ForeignKey(TestExecutions, models.DO_NOTHING, blank=True, null=True)
    iteration_number = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    result = models.CharField(max_length=20)
    failure_reason = models.TextField(blank=True, null=True)
    job_uid = models.CharField(max_length=255, blank=True, null=True)
    result_id = models.CharField(max_length=255, blank=True, null=True)
    release = models.ForeignKey('Releases', on_delete=models.DO_NOTHING, 
                               db_column='release_id', blank=True, null=True)
    testcase_ref = models.ForeignKey('TestCases', on_delete=models.DO_NOTHING,
                                    db_column='testcase_number', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test_iterations'

    @property
    def get_result_url(self):
        if self.result_id:
            return f"https://innowave.stb-tester.com/app/#/results?filter=job:{self.job_uid}&tz=Asia/Calcutta&selected_result={self.result_id}"
        return ''
