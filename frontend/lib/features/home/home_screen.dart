import 'package:flutter/material.dart';

import '../../domain/models/coupon.dart';
import '../../domain/models/recommendation.dart';
import '../../infrastructure/location/location_gateway.dart';
import '../../infrastructure/recommendations/recommendation_repository.dart';

const _accent = Color(0xFFFDB846);
const _accentDark = Color(0xFFE99E22);
const _ink = Color(0xFF202020);

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.repository,
    required this.locationGateway,
  });

  final RecommendationRepository repository;
  final LocationGateway locationGateway;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final Future<List<Coupon>> _coupons = widget.repository.loadCoupons();
  Recommendation? _recommendation;
  LocationAccessResult? _locationResult;
  bool _loading = false;
  bool _locationLoading = true;
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _requestLocationAtStartup();
    });
  }

  Future<void> _requestLocationAtStartup() async {
    setState(() => _locationLoading = true);
    final result = await widget.locationGateway.requestAtStartup();
    if (!mounted) return;
    setState(() {
      _locationResult = result;
      _locationLoading = false;
    });
  }

  Future<void> _handleLocationAction() async {
    final status = _locationResult?.status;
    if (status == LocationAccessStatus.deniedForever ||
        status == LocationAccessStatus.serviceDisabled) {
      final opened = await widget.locationGateway.openRelevantSettings(status!);
      if (!opened && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('브라우저 또는 기기 설정에서 위치 권한을 확인해 주세요.')),
        );
      }
    }
    if (!mounted) return;
    setState(() => _locationLoading = true);
    final result = await widget.locationGateway.refresh();
    if (!mounted) return;
    setState(() {
      _locationResult = result;
      _locationLoading = false;
    });
  }

  Future<void> _requestRecommendation() async {
    final location = _locationResult?.location;
    if (location == null) {
      await _handleLocationAction();
      return;
    }
    setState(() => _loading = true);
    try {
      final result = await widget.repository.recommend(
        purchaseAmount: 10000,
        latitude: location.latitude,
        longitude: location.longitude,
      );
      if (!mounted) return;
      setState(() => _recommendation = result);
    } on RecommendationException catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.message)));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showPreparing(String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$feature 기능은 다음 API 연동 단계에서 제공됩니다.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: IndexedStack(
          index: _selectedIndex,
          children: [
            _HomeTab(
              coupons: _coupons,
              recommendation: _recommendation,
              loading: _loading,
              locationLoading: _locationLoading,
              locationResult: _locationResult,
              onRecommend: _requestRecommendation,
              onLocationAction: _handleLocationAction,
              onPreparing: _showPreparing,
            ),
            _PlaceholderTab(
              icon: Icons.explore_outlined,
              title: '주변 혜택',
              description: '공공데이터 기반 가맹점 검색과 지도 화면이 연결될 자리입니다.',
            ),
            _PlaceholderTab(
              icon: Icons.confirmation_number_outlined,
              title: '내 쿠폰',
              description: '쿠폰 이미지 등록, OCR 인식, 유효기간 관리를 연결할 자리입니다.',
            ),
            _PlaceholderTab(
              icon: Icons.person_outline,
              title: '마이',
              description: '보유 카드·통신사와 알림 설정을 관리할 자리입니다.',
            ),
          ],
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) =>
            setState(() => _selectedIndex = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: '홈',
          ),
          NavigationDestination(
            icon: Icon(Icons.explore_outlined),
            selectedIcon: Icon(Icons.explore),
            label: '주변',
          ),
          NavigationDestination(
            icon: Icon(Icons.confirmation_number_outlined),
            selectedIcon: Icon(Icons.confirmation_number),
            label: '쿠폰',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: '마이',
          ),
        ],
      ),
    );
  }
}

class _HomeTab extends StatelessWidget {
  const _HomeTab({
    required this.coupons,
    required this.recommendation,
    required this.loading,
    required this.locationLoading,
    required this.locationResult,
    required this.onRecommend,
    required this.onLocationAction,
    required this.onPreparing,
  });

  final Future<List<Coupon>> coupons;
  final Recommendation? recommendation;
  final bool loading;
  final bool locationLoading;
  final LocationAccessResult? locationResult;
  final VoidCallback onRecommend;
  final VoidCallback onLocationAction;
  final ValueChanged<String> onPreparing;

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 10),
            child: Row(
              children: [
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '쿠폰콕',
                        style: TextStyle(
                          fontSize: 25,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                      SizedBox(height: 2),
                      Text(
                        '오늘도 혜택을 콕 집어드려요',
                        style: TextStyle(color: Colors.black54),
                      ),
                    ],
                  ),
                ),
                _RoundIconButton(
                  icon: Icons.notifications_none_rounded,
                  onTap: () => onPreparing('혜택 알림'),
                ),
              ],
            ),
          ),
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: TextField(
              readOnly: true,
              onTap: () => onPreparing('매장·혜택 검색'),
              decoration: const InputDecoration(
                hintText: '매장이나 혜택을 검색해 보세요',
                prefixIcon: Icon(Icons.search_rounded),
              ),
            ),
          ),
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
            child: _BenefitHero(
              loading: loading,
              locationLoading: locationLoading,
              locationResult: locationResult,
              onRecommend: onRecommend,
              onLocationAction: onLocationAction,
            ),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 26)),
        const SliverToBoxAdapter(
          child: _SectionHeader(title: '어떤 혜택을 찾으세요?', subtitle: '업종별 보기'),
        ),
        SliverToBoxAdapter(
          child: SizedBox(
            height: 106,
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              scrollDirection: Axis.horizontal,
              children: const [
                _CategoryChip(
                  icon: Icons.local_cafe_outlined,
                  label: '카페',
                  color: Color(0xFFFFE0B2),
                ),
                _CategoryChip(
                  icon: Icons.restaurant_outlined,
                  label: '음식점',
                  color: Color(0xFFFFCDD2),
                ),
                _CategoryChip(
                  icon: Icons.shopping_bag_outlined,
                  label: '쇼핑',
                  color: Color(0xFFD1C4E9),
                ),
                _CategoryChip(
                  icon: Icons.local_convenience_store_outlined,
                  label: '편의점',
                  color: Color(0xFFC8E6C9),
                ),
                _CategoryChip(
                  icon: Icons.movie_outlined,
                  label: '문화',
                  color: Color(0xFFBBDEFB),
                ),
              ],
            ),
          ),
        ),
        const SliverToBoxAdapter(child: SizedBox(height: 14)),
        SliverToBoxAdapter(
          child: FutureBuilder<List<Coupon>>(
            future: coupons,
            builder: (context, snapshot) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _SectionHeader(
                    title: '내 쿠폰',
                    subtitle: snapshot.hasData
                        ? '${snapshot.data!.length}장 보유'
                        : '불러오는 중',
                    action: '쿠폰 등록',
                    onAction: () => onPreparing('쿠폰 이미지 등록'),
                  ),
                  const SizedBox(height: 12),
                  if (!snapshot.hasData)
                    const Center(child: CircularProgressIndicator())
                  else
                    SizedBox(
                      height: 184,
                      child: ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 20),
                        scrollDirection: Axis.horizontal,
                        itemCount: snapshot.data!.length,
                        separatorBuilder: (_, _) => const SizedBox(width: 14),
                        itemBuilder: (_, index) =>
                            _CouponCard(coupon: snapshot.data![index]),
                      ),
                    ),
                ],
              );
            },
          ),
        ),
        if (recommendation != null) ...[
          const SliverToBoxAdapter(child: SizedBox(height: 28)),
          const SliverToBoxAdapter(
            child: _SectionHeader(title: '쿠폰콕 추천', subtitle: '최적 조합'),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
              child: _RecommendationCard(recommendation: recommendation!),
            ),
          ),
        ],
        const SliverToBoxAdapter(child: SizedBox(height: 36)),
      ],
    );
  }
}

class _BenefitHero extends StatelessWidget {
  const _BenefitHero({
    required this.loading,
    required this.locationLoading,
    required this.locationResult,
    required this.onRecommend,
    required this.onLocationAction,
  });

  final bool loading;
  final bool locationLoading;
  final LocationAccessResult? locationResult;
  final VoidCallback onRecommend;
  final VoidCallback onLocationAction;

  bool get _locationGranted => locationResult?.isGranted ?? false;

  String get _locationLabel {
    if (locationLoading) return '현재 위치 확인 중...';
    return locationResult?.message ?? '위치 권한을 확인해 주세요.';
  }

  String get _buttonLabel {
    if (locationLoading) return '위치 확인 중...';
    if (loading) return '계산 중...';
    if (!_locationGranted) return '위치 권한 다시 확인';
    return '10,000원 혜택 비교';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [_accent, Color(0xFFFFD36A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(26),
        boxShadow: const [
          BoxShadow(
            color: Color(0x33E99E22),
            blurRadius: 24,
            offset: Offset(0, 12),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined, size: 18),
                    const SizedBox(width: 5),
                    Expanded(
                      child: Text(
                        _locationLabel,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                const Text(
                  '10,000원 결제,\n가장 싸게 콕!',
                  style: TextStyle(
                    fontSize: 25,
                    height: 1.12,
                    fontWeight: FontWeight.w900,
                    color: _ink,
                  ),
                ),
                const SizedBox(height: 18),
                FilledButton.icon(
                  onPressed: locationLoading || loading
                      ? null
                      : _locationGranted
                      ? onRecommend
                      : onLocationAction,
                  icon: locationLoading || loading
                      ? const SizedBox.square(
                          dimension: 17,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(
                          _locationGranted
                              ? Icons.auto_awesome_rounded
                              : Icons.my_location_rounded,
                          size: 18,
                        ),
                  label: Text(_buttonLabel),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Container(
            width: 88,
            height: 116,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.72),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.savings_outlined,
              size: 54,
              color: _accentDark,
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.title,
    required this.subtitle,
    this.action,
    this.onAction,
  });

  final String title;
  final String subtitle;
  final String? action;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 22,
            decoration: BoxDecoration(
              color: _accent,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              title,
              style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w800),
            ),
          ),
          if (action != null)
            TextButton(onPressed: onAction, child: Text(action!))
          else
            Text(
              subtitle,
              style: const TextStyle(color: Colors.black45, fontSize: 13),
            ),
        ],
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  const _CategoryChip({
    required this.icon,
    required this.label,
    required this.color,
  });

  final IconData icon;
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 5),
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(icon, color: _ink),
          ),
          const SizedBox(height: 8),
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _CouponCard extends StatelessWidget {
  const _CouponCard({required this.coupon});

  final Coupon coupon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 244,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFFF0F0F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF3D4),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Icon(
                  Icons.local_cafe_outlined,
                  color: _accentDark,
                ),
              ),
              const Spacer(),
              const Icon(Icons.bookmark_border_rounded, color: Colors.black38),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            coupon.brand,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 3),
          Text(
            coupon.productName,
            style: const TextStyle(color: Colors.black54),
          ),
          const Spacer(),
          Row(
            children: [
              Text(
                '${_won(coupon.faceValue)}원',
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  color: _accentDark,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '~ ${coupon.expiryLabel}',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  textAlign: TextAlign.end,
                  style: const TextStyle(fontSize: 12, color: Colors.black45),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard({required this.recommendation});

  final Recommendation recommendation;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _ink,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.verified_rounded, color: _accent),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${recommendation.storeName} · ${recommendation.distanceMeters}m',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          const Text('예상 결제금액', style: TextStyle(color: Colors.white60)),
          Text(
            '${_won(recommendation.finalPrice)}원',
            style: const TextStyle(
              color: _accent,
              fontSize: 32,
              fontWeight: FontWeight.w900,
            ),
          ),
          Text(
            '총 ${_won(recommendation.saving)}원 절약',
            style: const TextStyle(color: Colors.white),
          ),
          const Divider(height: 30, color: Colors.white24),
          ...recommendation.components.map(
            (item) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      item.label,
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ),
                  Text(
                    '-${_won(item.amount)}원',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            recommendation.sourceTitle,
            style: const TextStyle(color: Colors.white38, fontSize: 12),
          ),
        ],
      ),
    );
  }
}

class _RoundIconButton extends StatelessWidget {
  const _RoundIconButton({required this.icon, required this.onTap});

  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return IconButton.filledTonal(onPressed: onTap, icon: Icon(icon));
  }
}

class _PlaceholderTab extends StatelessWidget {
  const _PlaceholderTab({
    required this.icon,
    required this.title,
    required this.description,
  });

  final IconData icon;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: const Color(0xFFFFF3D4),
                borderRadius: BorderRadius.circular(28),
              ),
              child: Icon(icon, size: 40, color: _accentDark),
            ),
            const SizedBox(height: 20),
            Text(
              title,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            Text(
              description,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.black54, height: 1.5),
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
