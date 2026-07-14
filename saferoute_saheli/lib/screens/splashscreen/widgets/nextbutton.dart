Positioned(
  bottom: 40,
  right: 24,
  child: ElevatedButton(
    onPressed: () {
      context.read<OnboardingBloc>().add(NextPageEvent());
    },
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.white,
      foregroundColor: Colors.black,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(30),
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: 28,
        vertical: 14,
      ),
    ),
    child: const Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          "Next",
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        SizedBox(width: 8),
        Icon(Icons.arrow_forward),
      ],
    ),
  ),
),