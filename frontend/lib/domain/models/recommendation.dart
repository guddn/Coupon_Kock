class SavingComponent {
  const SavingComponent({required this.label, required this.amount});

  final String label;
  final int amount;
}

class Recommendation {
  const Recommendation({
    required this.storeName,
    required this.distanceMeters,
    required this.purchaseAmount,
    required this.finalPrice,
    required this.components,
    required this.sourceTitle,
  });

  final String storeName;
  final int distanceMeters;
  final int purchaseAmount;
  final int finalPrice;
  final List<SavingComponent> components;
  final String sourceTitle;

  int get saving => purchaseAmount - finalPrice;
}
