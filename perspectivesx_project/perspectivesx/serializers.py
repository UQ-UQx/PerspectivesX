from rest_framework import serializers
from models import *

class TemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Template
        fields = '__all__'

class TemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateItem
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class LearnerPespectiveSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerPerspectiveSubmission
        fields = '__all__'


class LearnerSubmissionItemSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source = "__unicode__")
    class Meta:
        model = LearnerSubmissionItem
        fields = '__all__'
        read_only_fields = ('description',)


class CuratedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuratedItem
        fields = '__all__'

class SubmissionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionScore
        fields= '__all__'