import 'package:flutter/material.dart';

import '../../domain/models/coupon.dart';
import '../../infrastructure/recommendations/recommendation_repository.dart';

class CouponScreen extends StatelessWidget {
  const CouponScreen({
    super.key,
    required this.coupons,
    required this.onCreate,
  });

  final Future<List<Coupon>> coupons;
  final Future<void> Function(CouponDraft draft) onCreate;

  Future<void> _openRegistration(BuildContext context) async {
    final draft = await showModalBottomSheet<CouponDraft>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (_) => const _CouponRegistrationSheet(),
    );
    if (draft == null || !context.mounted) return;
    try {
      await onCreate(draft);
      if (!context.mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('쿠폰이 등록되었습니다.')));
    } on RecommendationException catch (error) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          '내 쿠폰',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          TextButton.icon(
            onPressed: () => _openRegistration(context),
            icon: const Icon(Icons.add_rounded),
            label: const Text('등록'),
          ),
        ],
      ),
      body: FutureBuilder<List<Coupon>>(
        future: coupons,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _Message(
              icon: Icons.cloud_off_outlined,
              title: '쿠폰을 불러오지 못했어요',
              description: '${snapshot.error}',
            );
          }
          final items = snapshot.data ?? const <Coupon>[];
          if (items.isEmpty) {
            return _Message(
              icon: Icons.confirmation_number_outlined,
              title: '등록된 쿠폰이 없어요',
              description: '브랜드, 상품명, 금액과 유효기간을 입력해 첫 쿠폰을 등록해 보세요.',
              action: FilledButton.icon(
                onPressed: () => _openRegistration(context),
                icon: const Icon(Icons.add_rounded),
                label: const Text('쿠폰 등록'),
              ),
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(20),
            itemCount: items.length,
            separatorBuilder: (_, _) => const SizedBox(height: 12),
            itemBuilder: (_, index) => _CouponTile(coupon: items[index]),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openRegistration(context),
        icon: const Icon(Icons.add_rounded),
        label: const Text('쿠폰 등록'),
      ),
    );
  }
}

class _CouponRegistrationSheet extends StatefulWidget {
  const _CouponRegistrationSheet();

  @override
  State<_CouponRegistrationSheet> createState() =>
      _CouponRegistrationSheetState();
}

class _CouponRegistrationSheetState extends State<_CouponRegistrationSheet> {
  final _formKey = GlobalKey<FormState>();
  final _brandController = TextEditingController();
  final _productController = TextEditingController();
  final _valueController = TextEditingController();
  DateTime? _expiryDate;

  @override
  void dispose() {
    _brandController.dispose();
    _productController.dispose();
    _valueController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final selected = await showDatePicker(
      context: context,
      initialDate: _expiryDate ?? now.add(const Duration(days: 90)),
      firstDate: DateTime(now.year, now.month, now.day),
      lastDate: DateTime(now.year + 10),
    );
    if (selected != null) setState(() => _expiryDate = selected);
  }

  void _submit() {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_expiryDate == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('유효기간을 선택해 주세요.')));
      return;
    }
    Navigator.pop(
      context,
      CouponDraft(
        brand: _brandController.text.trim(),
        productName: _productController.text.trim(),
        faceValue: int.parse(_valueController.text.replaceAll(',', '')),
        expiryDate: _expiryDate!,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final bottom = MediaQuery.viewInsetsOf(context).bottom;
    return SingleChildScrollView(
      padding: EdgeInsets.fromLTRB(20, 18, 20, 24 + bottom),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              '쿠폰 등록',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 6),
            const Text('PIN·바코드는 입력하거나 서버로 전송하지 않습니다.'),
            const SizedBox(height: 22),
            TextFormField(
              controller: _brandController,
              decoration: const InputDecoration(
                labelText: '브랜드',
                prefixIcon: Icon(Icons.storefront_outlined),
              ),
              validator: (value) => value == null || value.trim().isEmpty
                  ? '브랜드를 입력해 주세요.'
                  : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _productController,
              decoration: const InputDecoration(
                labelText: '상품명',
                prefixIcon: Icon(Icons.card_giftcard_outlined),
              ),
              validator: (value) => value == null || value.trim().isEmpty
                  ? '상품명을 입력해 주세요.'
                  : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _valueController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '쿠폰 금액',
                suffixText: '원',
                prefixIcon: Icon(Icons.payments_outlined),
              ),
              validator: (value) {
                final parsed = int.tryParse((value ?? '').replaceAll(',', ''));
                return parsed == null || parsed < 0 ? '올바른 금액을 입력해 주세요.' : null;
              },
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _pickDate,
              icon: const Icon(Icons.event_outlined),
              label: Text(
                _expiryDate == null ? '유효기간 선택' : '유효기간 ${_date(_expiryDate!)}',
              ),
            ),
            const SizedBox(height: 20),
            FilledButton(onPressed: _submit, child: const Text('등록 완료')),
          ],
        ),
      ),
    );
  }
}

class _CouponTile extends StatelessWidget {
  const _CouponTile({required this.coupon});

  final Coupon coupon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: const CircleAvatar(
          child: Icon(Icons.confirmation_number_outlined),
        ),
        title: Text(
          coupon.brand,
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        subtitle: Text('${coupon.productName}\n~ ${coupon.expiryLabel}'),
        isThreeLine: true,
        trailing: Text(
          '${_formatNumber(coupon.faceValue)}원',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
    );
  }
}

class _Message extends StatelessWidget {
  const _Message({
    required this.icon,
    required this.title,
    required this.description,
    this.action,
  });
  final IconData icon;
  final String title;
  final String description;
  final Widget? action;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 64, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 18),
          Text(
            title,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          Text(description, textAlign: TextAlign.center),
          if (action != null) ...[const SizedBox(height: 18), action!],
        ],
      ),
    ),
  );
}

String _date(DateTime value) =>
    '${value.year}.${value.month.toString().padLeft(2, '0')}.${value.day.toString().padLeft(2, '0')}';
String _formatNumber(int value) => value.toString().replaceAllMapped(
  RegExp(r'\B(?=(\d{3})+(?!\d))'),
  (_) => ',',
);
