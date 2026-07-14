import 'package:flutter/material.dart';

class NextButton extends StatelessWidget {

  final VoidCallback onPressed;

  const NextButton({
    super.key,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {

    return SizedBox(
      width: double.infinity,
      height: 55,
      child: ElevatedButton(

        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.deepPurple,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
        ),

        onPressed: onPressed,

        child: const Text(
          "Next",
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
          ),
        ),

      ),
    );
  }
}