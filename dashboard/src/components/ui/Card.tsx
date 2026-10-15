import React from 'react';

interface CardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerBorder?: boolean;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  icon,
  action,
  children,
  className = '',
  headerBorder = true,
}) => {
  return (
    <div className={`bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow duration-200 ${className}`}>
      {(title || action || icon) && (
        <div className={`px-5 py-4 flex items-center justify-between ${headerBorder ? 'border-b border-slate-100' : ''}`}>
          <div className="flex items-center gap-3">
            {icon && (
              <div className="p-2 rounded-xl bg-teal-50 text-teal-600">
                {icon}
              </div>
            )}
            <div>
              {title && <h3 className="font-semibold text-slate-800 text-sm tracking-tight">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
};
