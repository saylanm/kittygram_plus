from rest_framework import serializers

from .models import Cat, Owner, Achievement, AchievementCat, CHOICES


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True)
    age = serializers.SerializerMethodField()
    # Теперь поле примет только значение, упомянутое в списке CHOICES
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements',
                  'age')


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')


def create(self, validated_data):
    if 'achievements' not in self.initial_data:
        # То создаём запись о котике без его достижений
        cat = Cat.objects.create(**validated_data)
        return cat

    # Иначе делаем следующее:
    # Уберём список достижений из словаря validated_data и сохраним его
    achievements = validated_data.pop('achievements')
    # Сначала добавляем котика в БД
    cat = Cat.objects.create(**validated_data)
    # А потом добавляем его достижения в БД
    for achievement in achievements:
        current_achievement, status = Achievement.objects.get_or_create(
            **achievement)
        # И связываем каждое достижение с этим котиком
        AchievementCat.objects.create(
            achievement=current_achievement, cat=cat)
    return cat
