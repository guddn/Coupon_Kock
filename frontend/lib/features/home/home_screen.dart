import 'package:flutter/material.dart';

import '../../domain/models/coupon.dart';
import '../../domain/models/recommendation.dart';
import '../../infrastructure/recommendations/recommendation_repository.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    this.repository = const DemoRecommendationRepository(),
  });

  final RecommendationRepository repository;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final Future<List<Coupon>> _coupons = widget.repository.loadCoupons();
  Recommendation? _recommendation;
  bool _loading = false;

  Future<void> _requestRecommendation() async {
    setState(() => _loading = true);
    final result = await widget.repository.recommend(purchaseAmount: 10000);
    if (!mounted) return;
    setState(() {
      _recommendation = result;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Coupon Knock'),
        actions: [
          IconButton(
            tooltip: '프로필',
            onPressed: () {},
            icon: const Icon(Icons.account_circle_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
          children: [
            Text(
              '지금 쓸 수 있는 혜택을\n한 번에 확인하세요',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w800,
                height: 1.2,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '위치, 보유 쿠폰, 공식 카드·통신사 조건을 함께 비교합니다.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 24),
            _LocationCard(
              onRecommend: _requestRecommendation,
              loading: _loading,
            ),
            const SizedBox(height: 24),
            const _SectionTitle(title: '내 쿠폰', action: '이미지로 등록'),
            const SizedBox(height: 12),
            FutureBuilder<List<Coupon>>(
              future: _coupons,
              builder: (context, snapshot) {
                if (!snapshot.hasData) {
                  return const Center(child: CircularProgressIndicator());
                }
                return Column(
                  children: snapshot.data!
                      .map((coupon) => _CouponCard(coupon: coupon))
                      .toList(),
                );
              },
            ),
            if (_recommendation != null) ...[
              const SizedBox(height: 24),
              const _SectionTitle(title: '추천 결과'),
              const SizedBox(height: 12),
              _RecommendationCard(recommendation: _recommendation!),
            ],
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        icon: const Icon(Icons.add_a_photo_outlined),
        label: const Text('쿠폰 등록'),
      ),
    );
  }
}

class _LocationCard extends StatelessWidget {
  const _LocationCard({required this.onRecommend, required this.loading});

  final VoidCallback onRecommend;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.location_on_outlined),
                SizedBox(width: 8),
                Text('데모 위치 · 아주대학교'),
              ],
            ),
            const SizedBox(height: 12),
            const Text('지원 매장이 반경 100m 안에 있습니다.'),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: loading ? null : onRecommend,
              icon: loading
                  ? const SizedBox.square(
                      dimension: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(loading ? '계산 중...' : '10,000원 혜택 비교'),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, this.action});

  final String title;
  final String? action;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: Theme.of(context).textTheme.titleLarge),
        if (action != null) TextButton(onPressed: () {}, child: Text(action!)),
      ],
    );
  }
}

class _CouponCard extends StatelessWidget {
  const _CouponCard({required this.coupon});

  final Coupon coupon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: Theme.of(context).colorScheme.secondaryContainer,
          child: const Icon(Icons.confirmation_number_outlined),
        ),
        title: Text('${coupon.brand} · ${coupon.productName}'),
        subtitle: Text('유효기간 ${coupon.expiryLabel}'),
        trailing: Text(
          '${_won(coupon.faceValue)}원',
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard({required this.recommendation});

  final Recommendation recommendation;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${recommendation.storeName} · ${recommendation.distanceMeters}m',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            Text('예상 결제금액', style: Theme.of(context).textTheme.labelLarge),
            Text(
              '${_won(recommendation.finalPrice)}원',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.w800,
              ),
            ),
            Text('총 ${_won(recommendation.saving)}원 절약'),
            const Divider(height: 32),
            ...recommendation.components.map(
              (item) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [Text(item.label), Text('-${_won(item.amount)}원')],
                ),
              ),
            ),
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.verified_outlined, size: 18),
                const SizedBox(width: 8),
                Expanded(child: Text(recommendation.sourceTitle)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _won(int value) {
  final digits = value.toString();
  return digits.replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (_) => ',');
}
