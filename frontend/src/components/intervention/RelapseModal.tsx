import { useState } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { useUserState } from '../../state/UserStateContext';
import { HeartHandshake, CheckCircle2 } from 'lucide-react';

export interface RelapseModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RelapseModal = ({ isOpen, onClose }: RelapseModalProps) => {
  const { recordRelapse } = useUserState();

  const [trigger, setTrigger] = useState<string>('ضغط عصبي أو موقف مفاجئ');
  const [context] = useState<string>('مع الأصدقاء أو في العمل');
  const [cigarettesCount, setCigarettesCount] = useState<number>(1);
  const [cravingIntensity, setCravingIntensity] = useState<number>(8);
  const [actionPlan, setActionPlan] = useState<string>('الاستمرار في الخطة وتفادي نفس الموقف غداً');
  const [isSaved, setIsSaved] = useState<boolean>(false);

  const triggersList = [
    'ضغط عصبي أو موقف مفاجئ',
    'تجمع مع مدخنين',
    'شعور بالملل أو الوحدة',
    'تناول وجبة ثقيلة أو قهوة',
    'دافع الفضول أو التجربة',
  ];

  const handleSave = () => {
    recordRelapse({
      trigger,
      context,
      cigarettesCount,
      cravingIntensity,
      actionPlan,
    });
    setIsSaved(true);
  };

  const handleClose = () => {
    setIsSaved(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="حصلت كبوة؟ سالم معاك ومش بيحكم عليك"
      subtitle="التعافي رحلة بتمر بمنعطفات، والمهم هو كيف نكمل من النقطة دي"
      maxWidth="md"
    >
      <div className="flex flex-col gap-5 font-arabic" dir="rtl">
        {!isSaved ? (
          <div className="flex flex-col gap-4">
            {/* Compassionate Message Box */}
            <div className="p-4 rounded-2xl bg-[#2D8BFF]/5 border border-[#2D8BFF]/20 flex items-start gap-3">
              <HeartHandshake className="w-5 h-5 text-[#2D8BFF] shrink-0 mt-0.5" />
              <p className="text-xs text-[#061A3A] leading-relaxed">
                التدخين بعد فترة توقف مش معناه إنك فشلت أو رجعت للصفر. كل يوم كسبته لسه في رصيد صحتك. خلينا نفهم اللي حصل ونحدد الخطوة الجاية.
              </p>
            </div>

            {/* Trigger Selector */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-[#061A3A]">إيه المحفز الأساسي اللي أدى للموقف؟</label>
              <div className="flex flex-col gap-1.5">
                {triggersList.map((trig) => (
                  <button
                    key={trig}
                    type="button"
                    onClick={() => setTrigger(trig)}
                    className={`
                      p-3 rounded-xl border text-right text-xs transition-all duration-150 cursor-pointer
                      ${
                        trigger === trig
                          ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A]'
                          : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                      }
                    `}
                  >
                    {trig}
                  </button>
                ))}
              </div>
            </div>

            {/* Count & Intensity */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-bold text-[#061A3A]">عدد السجائر</label>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 5].map((cnt) => (
                    <button
                      key={cnt}
                      type="button"
                      onClick={() => setCigarettesCount(cnt)}
                      className={`
                        flex-1 h-10 rounded-xl border text-xs font-bold transition-all duration-150 cursor-pointer
                        ${
                          cigarettesCount === cnt
                            ? 'bg-[#2D8BFF] text-white border-[#2D8BFF]'
                            : 'bg-[#F4F7FB] border-[#D9E2F0] text-[#061A3A]'
                        }
                      `}
                    >
                      {cnt}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-bold text-[#061A3A]">شدة الرغبة (1-10)</label>
                <div className="flex items-center gap-1.5">
                  {[5, 7, 9, 10].map((int) => (
                    <button
                      key={int}
                      type="button"
                      onClick={() => setCravingIntensity(int)}
                      className={`
                        flex-1 h-10 rounded-xl border text-xs font-bold transition-all duration-150 cursor-pointer
                        ${
                          cravingIntensity === int
                            ? 'bg-[#1E3A8A] text-white border-[#1E3A8A]'
                            : 'bg-[#F4F7FB] border-[#D9E2F0] text-[#061A3A]'
                        }
                      `}
                    >
                      {int}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Next Action Commitment */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-[#061A3A]">خطوتك الجاية للتعامل:</label>
              <div className="flex flex-col gap-1.5">
                {[
                  'الاستمرار في الخطة وتفادي نفس المحفز غداً',
                  'شرب ماء والبدء في تمرين التنفس مباشرة',
                  'التحدث مع سالم لإعادة صياغة الخطة اليومية',
                ].map((act) => (
                  <button
                    key={act}
                    type="button"
                    onClick={() => setActionPlan(act)}
                    className={`
                      p-3 rounded-xl border text-right text-xs transition-all duration-150 cursor-pointer
                      ${
                        actionPlan === act
                          ? 'border-[#2D8BFF] bg-[#2D8BFF]/5 font-bold text-[#1E3A8A]'
                          : 'border-[#D9E2F0] bg-[#F4F7FB] text-[#061A3A] hover:border-[#C4D1E3]'
                      }
                    `}
                  >
                    {act}
                  </button>
                ))}
              </div>
            </div>

            <Button variant="primary" size="lg" fullWidth onClick={handleSave}>
              حفظ واستئناف الخطة مع سالم
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center text-center gap-4 py-4">
            <div className="w-16 h-16 rounded-full bg-[#34D399]/15 text-[#047857] flex items-center justify-center">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div className="flex flex-col gap-1.5 max-w-sm">
              <h4 className="text-base font-bold text-[#061A3A]">
                تم تحديث الخطة، وأنت على الطريق الصحيح
              </h4>
              <p className="text-xs text-[#5F708C] leading-relaxed">
                الاعتراف بالخطوة وتحليلها هو سر النجاح على المدى الطويل. سالم معاك في كل خطوة قادمة.
              </p>
            </div>

            <Button variant="primary" size="lg" fullWidth onClick={handleClose}>
              العودة للرئيسية
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};
