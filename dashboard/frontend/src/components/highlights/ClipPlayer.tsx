interface Props {
  eventId: string;
}

export default function ClipPlayer({ eventId }: Props) {
  return (
    <video
      controls
      className="w-full aspect-video bg-black"
      src={`/api/highlights/${eventId}/download`}
    >
      Your browser does not support video playback.
    </video>
  );
}
