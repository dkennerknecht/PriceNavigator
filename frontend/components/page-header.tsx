import Link from "next/link";

type PageHeaderProps = {
  title: string;
  description: string;
  actions?: Array<{ href: string; label: string; variant?: "primary" | "ghost" }>;
};

export function PageHeader({ title, description, actions = [] }: PageHeaderProps) {
  return (
    <div className="page-header">
      <div>
        <p className="eyebrow">PriceNavigator</p>
        <h1>{title}</h1>
        <p className="muted">{description}</p>
      </div>
      <div className="page-actions">
        {actions.map((action) => (
          <Link
            key={action.href}
            className={action.variant === "ghost" ? "button button-ghost" : "button"}
            href={action.href}
          >
            {action.label}
          </Link>
        ))}
      </div>
    </div>
  );
}

