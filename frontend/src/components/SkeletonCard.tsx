export const SkeletonCard = () => (
  <div className="rounded-2xl border border-zinc-800 bg-background-card overflow-hidden animate-pulse">
    <div className="h-44 bg-zinc-800" />
    <div className="p-4 space-y-3">
      <div className="h-4 bg-zinc-700 rounded w-3/4" />
      <div className="h-3 bg-zinc-800 rounded w-1/2" />
      <div className="h-3 bg-zinc-800 rounded w-2/3" />
      <div className="flex justify-between items-center pt-2">
        <div className="h-5 bg-zinc-700 rounded w-1/4" />
        <div className="h-8 bg-zinc-800 rounded-lg w-1/3" />
      </div>
    </div>
  </div>
);

export const SkeletonDetailHeader = () => (
  <div className="animate-pulse space-y-6">
    {/* Hero skeleton */}
    <div className="rounded-2xl overflow-hidden border border-zinc-800 bg-background-card">
      <div className="h-56 bg-zinc-800" />
      <div className="p-8 space-y-4">
        <div className="h-3 bg-zinc-700 rounded w-1/4" />
        <div className="h-8 bg-zinc-700 rounded w-3/4" />
        <div className="h-4 bg-zinc-800 rounded w-full" />
        <div className="h-4 bg-zinc-800 rounded w-5/6" />
        <div className="flex gap-4 pt-2">
          <div className="h-6 bg-zinc-700 rounded w-1/5" />
          <div className="h-6 bg-zinc-700 rounded w-1/5" />
          <div className="h-6 bg-zinc-700 rounded w-1/5" />
        </div>
        <div className="h-12 bg-zinc-700 rounded-xl w-1/3 mt-4" />
      </div>
    </div>
    {/* Modules skeleton */}
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-14 bg-zinc-800 rounded-xl" />
      ))}
    </div>
  </div>
);

export default SkeletonCard;
