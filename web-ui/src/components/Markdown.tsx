import ReactMarkdown, { Components } from "react-markdown";

type MarkdownProps = {
  content: string;
};

const components: Components = {
  h1: ({ children }) => <h1 className="text-4xl font-semibold tracking-tight text-foreground">{children}</h1>,
  h2: ({ children }) => <h2 className="text-2xl font-semibold text-foreground pt-4">{children}</h2>,
  h3: ({ children }) => <h3 className="text-lg font-semibold text-foreground pt-3">{children}</h3>,
  p: ({ children }) => <p className="text-base leading-7 text-muted-foreground">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-6 space-y-2 text-muted-foreground">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-6 space-y-2 text-muted-foreground">{children}</ol>,
  li: ({ children }) => <li className="leading-7">{children}</li>,
  a: ({ children, href }) => (
    <a href={href} className="underline underline-offset-4 hover:text-foreground">
      {children}
    </a>
  ),
  strong: ({ children }) => <strong className="text-foreground font-semibold">{children}</strong>,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-border pl-4 text-muted-foreground">{children}</blockquote>
  ),
  hr: () => <hr className="border-border" />,
};

export function Markdown({ content }: MarkdownProps) {
  return <ReactMarkdown components={components}>{content}</ReactMarkdown>;
}

