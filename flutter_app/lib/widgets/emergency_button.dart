import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/app_colors.dart';

class EmergencyButton extends StatefulWidget {
  final VoidCallback onTrigger;
  final Duration holdDuration;

  const EmergencyButton({
    Key? key,
    required this.onTrigger,
    this.holdDuration = const Duration(milliseconds: 2000),
  }) : super(key: key);

  @override
  State<EmergencyButton> createState() => _EmergencyButtonState();
}

class _EmergencyButtonState extends State<EmergencyButton> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _scaleAnimation;
  Timer? _holdTimer;
  double _progress = 0.0;
  bool _isPressing = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);

    _scaleAnimation = Tween<double>(begin: 0.96, end: 1.04).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _holdTimer?.cancel();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    HapticFeedback.heavyImpact();
    setState(() {
      _isPressing = true;
      _progress = 0.0;
    });

    const stepMs = 50;
    final totalSteps = widget.holdDuration.inMilliseconds / stepMs;
    int currentStep = 0;

    _holdTimer = Timer.periodic(const Duration(milliseconds: stepMs), (timer) {
      currentStep++;
      if (mounted) {
        setState(() {
          _progress = (currentStep / totalSteps).clamp(0.0, 1.0);
        });
      }

      if (currentStep >= totalSteps) {
        timer.cancel();
        HapticFeedback.vibrate();
        widget.onTrigger();
        if (mounted) {
          setState(() {
            _isPressing = false;
            _progress = 0.0;
          });
        }
      }
    });
  }

  void _onTapUp(TapUpDetails details) {
    _cancelHold();
  }

  void _onTapCancel() {
    _cancelHold();
  }

  void _cancelHold() {
    _holdTimer?.cancel();
    if (mounted) {
      setState(() {
        _isPressing = false;
        _progress = 0.0;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    const size = 190.0;

    return Center(
      child: GestureDetector(
        onTapDown: _onTapDown,
        onTapUp: _onTapUp,
        onTapCancel: _onTapCancel,
        child: AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            final scale = _isPressing ? 0.95 : _scaleAnimation.value;
            return Transform.scale(
              scale: scale,
              child: child,
            );
          },
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Outer Glowing Aura Rings
              Container(
                width: size + 36,
                height: size + 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.emergency.withValues(alpha: _isPressing ? 0.25 : 0.12),
                ),
              ),
              Container(
                width: size + 18,
                height: size + 18,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.emergency.withValues(alpha: _isPressing ? 0.40 : 0.20),
                ),
              ),

              // Circular Hold Progress Indicator
              if (_isPressing)
                SizedBox(
                  width: size + 8,
                  height: size + 8,
                  child: CircularProgressIndicator(
                    value: _progress,
                    strokeWidth: 6,
                    valueColor: const AlwaysStoppedAnimation<Color>(AppColors.secondary),
                    backgroundColor: Colors.transparent,
                  ),
                ),

              // Solid Crimson Emergency Core
              Container(
                width: size,
                height: size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: AppColors.emergencyGradient,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.emergency.withValues(alpha: 0.45),
                      blurRadius: 24,
                      spreadRadius: 4,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.warning_amber_rounded,
                      color: AppColors.white,
                      size: 48,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _isPressing ? 'HOLDING...' : 'EMERGENCY',
                      style: const TextStyle(
                        color: AppColors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _isPressing ? '${((1.0 - _progress) * 2).toStringAsFixed(1)}s' : 'PRESS & HOLD',
                      style: TextStyle(
                        color: AppColors.white.withValues(alpha: 0.85),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
