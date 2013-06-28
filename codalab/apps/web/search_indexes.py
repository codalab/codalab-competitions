from haystack import indexes
from apps.web.models import Competition

class CompetitionIndex(indexes.SearchIndex, indexes.Indexable):
   text = indexes.CharField(document=True,use_template=True)
   
   def get_model(self):
      return Competition


