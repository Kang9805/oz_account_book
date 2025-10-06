from django.db import models
from django.conf import settings

# =============================================================
# ✨ 제공된 상수 목록 반영 ✨
# =============================================================

# 은행 코드 (BANK_CODES)
BANK_CHOICES = [
    ("000", "알수없음"), ("001", "한국은행"), ("002", "산업은행"), ("003", "기업은행"),
    ("004", "국민은행"), ("005", "외환은행"), ("007", "수협중앙회"), ("008", "수출입은행"),
    ("011", "농협은행"), ("012", "지역농.축협"), ("020", "우리은행"), ("023", "SC은행"),
    ("027", "한국씨티은행"), ("031", "대구은행"), ("032", "부산은행"), ("034", "광주은행"),
    ("035", "제주은행"), ("037", "전북은행"), ("039", "경남은행"), ("045", "새마을금고중앙회"),
    ("048", "신협중앙회"), ("050", "상호저축은행"), ("051", "중국은행"), ("052", "모건스탠리은행"),
    ("054", "HSBC은행"), ("055", "도이치은행"), ("056", "알비에스피엘씨은행"), ("057", "제이피모간체이스은행"),
    ("058", "미즈호은행"), ("059", "미쓰비시도쿄UFJ은행"), ("060", "BOA은행"), ("061", "비엔피파리바은행"),
    ("062", "중국공상은행"), ("063", "중국은행"), ("064", "산림조합중앙회"), ("065", "대화은행"),
    ("066", "교통은행"), ("071", "우체국"), ("076", "신용보증기금"), ("077", "기술보증기금"),
    ("081", "KEB하나은행"), ("088", "신한은행"), ("089", "케이뱅크"), ("090", "카카오뱅크"),
    ("092", "토스뱅크"), ("093", "한국주택금융공사"), ("094", "서울보증보험"), ("095", "경찰청"),
    ("096", "한국전자금융(주)"), ("099", "금융결제원"), ("102", "대신저축은행"), ("103", "에스비아이저축은행"),
    ("104", "에이치케이저축은행"), ("105", "웰컴저축은행"), ("106", "신한저축은행"), ("209", "유안타증권"),
    ("218", "현대증권"), ("221", "골든브릿지투자증권"), ("222", "한양증권"), ("223", "리딩투자증권"),
    ("224", "BNK투자증권"), ("225", "IBK투자증권"), ("226", "KB투자증권"), ("227", "KTB투자증권"),
    ("230", "미래에셋증권"), ("238", "대우증권"), ("240", "삼성증권"), ("243", "한국투자증권"),
    ("261", "교보증권"), ("262", "하이투자증권"), ("263", "HMC투자증권"), ("264", "키움증권"),
    ("265", "이베스트투자증권"), ("266", "SK증권"), ("267", "대신증권"), ("269", "한화투자증권"),
    ("270", "하나대투증권"), ("278", "신한금융투자"), ("279", "DB금융투자"), ("280", "유진투자증권"),
    ("287", "메리츠종합금융증권"), ("289", "NH투자증권"), ("290", "부국증권"), ("291", "신영증권"),
    ("292", "엘아이지투자증권"), ("293", "한국증권금융"), ("294", "펀드온라인코리아"), ("295", "우리종합금융"),
    ("296", "삼성선물"), ("297", "외환선물"), ("298", "현대선물"),
]

# 계좌 종류 (ACCOUNT_TYPE)
ACCOUNT_TYPE_CHOICES = [
    ("CHECKING", "입출금"),
    ("SAVING", "적금"),
    ("LOAN", "대출"),
    ("PENSION", "연금"),
    ("TRUST", "신탁"),
    ("FOREIGN_CURRENCY", "외화"),
    ("IRP", "퇴직연금"),
    ("STOCK", "주식"),
]

# 거래 타입 (TRANSACTION_TYPE)
TRANSACTION_TYPE_CHOICES = [
    ("DEPOSIT", "입금"),
    ("WITHDRAW", "출금"),
]

# 거래 종류 (TRANSACTION_METHOD)
PAYMENT_METHOD_CHOICES = [ # 기존 모델 필드명(PAYMENT_METHOD)에 맞춤
    ("ATM", "ATM 거래"),
    ("TRANSFER", "계좌이체"),
    ("AUTOMATIC_TRANSFER", "자동이체"),
    ("CARD", "카드결제"),
    ("INTEREST", "이자"),
]

# (도전 미션 관련 상수는 모델이 없으므로 일단 제외합니다. 필요시 Analysis 모델에 사용됩니다.)
# =============================================================


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name="소유자"
    )

    account_number = models.CharField(max_length=20, unique=True, verbose_name="계좌 번호")

    # 🌟 BANK_CHOICES 반영
    bank_code = models.CharField(max_length=3, choices=BANK_CHOICES, verbose_name="은행 코드")

    # 🌟 ACCOUNT_TYPE_CHOICES 반영
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='CHECKING', verbose_name="계좌 종류"
    )

    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name="현재 잔액")

    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "accounts"
        verbose_name = "계좌"
        verbose_name_plural = "계좌 목록"

    # get_bank_code_display() 메서드는 Django가 자동으로 생성해줍니다.
    def __str__(self):
        return f"[{self.get_bank_code_display()}] {self.account_number}"


class Transaction(models.Model):
    account = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="계좌"
    )

    transaction_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="거래 금액")

    post_transaction_amount = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="거래 후 잔액"
    )

    transaction_details = models.CharField(max_length=255, blank=True, verbose_name="거래 설명/인자 내역")

    # 🌟 TRANSACTION_TYPE_CHOICES 반영
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPE_CHOICES, verbose_name="입출금 타입"
    )

    # 🌟 PAYMENT_METHOD_CHOICES (거래 종류) 반영
    transaction_method = models.CharField( # 기존 필드명(transaction_method) 유지
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default='TRANSFER', verbose_name="거래 타입"
    )

    transaction_timestamp = models.DateTimeField(verbose_name="거래 일시")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "transaction_history"
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 내역 목록"
        ordering = ["-transaction_timestamp"]

    def __str__(self):
        return f"{self.account.account_number} | {self.transaction_type} {self.transaction_amount}"