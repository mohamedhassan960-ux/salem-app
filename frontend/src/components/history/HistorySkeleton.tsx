export const HistorySkeleton = () => {
  return (
    <div className="flex flex-col gap-3 font-arabic animate-pulse" dir="rtl">
      <div className="h-4 w-20 bg-[#E8EFF8] rounded-md mb-1" />
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="p-4 rounded-2xl bg-[#FFFFFF] border border-[#D9E2F0] flex items-center justify-between gap-3"
        >
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="w-10 h-10 rounded-xl bg-[#F4F7FB] shrink-0" />
            <div className="flex flex-col gap-2 flex-1 min-w-0">
              <div className="h-4 w-1/3 bg-[#E8EFF8] rounded" />
              <div className="h-3 w-2/3 bg-[#F4F7FB] rounded" />
            </div>
          </div>
          <div className="w-6 h-6 rounded-md bg-[#F4F7FB] shrink-0" />
        </div>
      ))}
    </div>
  );
};
