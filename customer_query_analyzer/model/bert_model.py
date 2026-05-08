import torch.nn as nn
from transformers import BertModel
from config.settings import BERT_BASE_MODEL, DROPOUT


class MultiTaskBERT(nn.Module):
    """
    BERT model with two classification heads:
    - Intent classifier  : 151 intents from CLINC150
    - Sentiment classifier: negative / neutral / positive
    """

    def __init__(self, num_intents, num_sentiments,
                 bert_name=BERT_BASE_MODEL, dropout=DROPOUT):
        super().__init__()
        self.bert    = BertModel.from_pretrained(bert_name)
        h            = self.bert.config.hidden_size
        self.dropout = nn.Dropout(dropout)

        self.intent_classifier = nn.Sequential(
            nn.Linear(h, 512),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(512, num_intents),
        )
        self.sentiment_classifier = nn.Sequential(
            nn.Linear(h, 256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_sentiments),
        )

    def forward(self, input_ids, attention_mask, token_type_ids):
        out = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )
        cls = self.dropout(out.pooler_output)
        return self.intent_classifier(cls), self.sentiment_classifier(cls)
