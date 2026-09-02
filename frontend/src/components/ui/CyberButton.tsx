import { useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

interface CyberButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  className?: string;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  id?: string;
  'aria-label'?: string;
}

export function CyberButton({
  children,
  onClick,
  href,
  variant = 'primary',
  className = '',
  disabled = false,
  type = 'button',
  id,
  'aria-label': ariaLabel,
}: CyberButtonProps) {
  const ref = useRef<HTMLButtonElement | HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 300, damping: 25 });
  const springY = useSpring(y, { stiffness: 300, damping: 25 });

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = (ref.current as HTMLElement)?.getBoundingClientRect();
    if (!rect || disabled) return;
    // Magnetic pull — small displacement toward cursor
    const dx = (e.clientX - (rect.left + rect.width / 2)) * 0.2;
    const dy = (e.clientY - (rect.top + rect.height / 2)) * 0.2;
    x.set(dx);
    y.set(dy);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const variantClass =
    variant === 'primary'   ? 'btn-primary'   :
    variant === 'secondary' ? 'btn-secondary' :
    variant === 'danger'    ? 'btn-danger'    :
                              'btn-ghost';

  const content = (
    <motion.div
      className="relative z-10 flex items-center justify-center gap-2"
      style={{ x: springX, y: springY }}
    >
      {children}
    </motion.div>
  );

  const sharedProps = {
    id,
    'aria-label': ariaLabel,
    className: `${variantClass} ${className} relative overflow-hidden`,
    onMouseMove: handleMouseMove,
    onMouseLeave: handleMouseLeave,
    style: { display: 'inline-flex', alignItems: 'center', justifyContent: 'center' },
  };

  if (href && !disabled) {
    return (
      <motion.a
        ref={ref as React.Ref<HTMLAnchorElement>}
        href={href}
        {...sharedProps}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        transition={{ type: 'spring', stiffness: 400, damping: 20 }}
      >
        {content}
      </motion.a>
    );
  }

  return (
    <motion.button
      ref={ref as React.Ref<HTMLButtonElement>}
      type={type}
      disabled={disabled}
      onClick={onClick}
      {...sharedProps}
      whileHover={disabled ? {} : { scale: 1.03 }}
      whileTap={disabled ? {} : { scale: 0.97 }}
      transition={{ type: 'spring', stiffness: 400, damping: 20 }}
    >
      {content}
    </motion.button>
  );
}
