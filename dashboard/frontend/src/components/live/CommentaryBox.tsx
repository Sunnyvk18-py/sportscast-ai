interface Props {
  text: string;
}

export default function CommentaryBox({ text }: Props) {
  return <p className="text-sm italic text-foreground/70 border-l-2 border-vision pl-3">{text}</p>;
}
