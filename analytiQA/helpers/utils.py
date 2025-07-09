from apps.core.models import TestPlan

def get_attribute(instance: TestPlan):
    x = [f.name for f in instance._meta.fields + instance._meta.many_to_many]
    print(x)


if __name__ == '__main__':
    test = TestPlan()

