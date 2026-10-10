// Mori: a floating desktop pet that shows your Monogamy vow.
// A borderless, always-on-top window hosting pet.html. It re-reads
// ~/.monogamy/state.json every 1.5s and pushes it into the page.

import Cocoa
import WebKit

final class PetWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { false }
}

final class PetWebView: WKWebView {
    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }
}

final class Pet: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate {
    var window: PetWindow!
    var web: PetWebView!
    var timer: Timer?
    var lastJSON: String?
    var dragOrigin = NSPoint.zero
    let smallSize = NSSize(width: 130, height: 160)

    var statePath: String {
        let home = ProcessInfo.processInfo.environment["MONOGAMY_HOME"] ?? (NSHomeDirectory() + "/.monogamy")
        return home + "/state.json"
    }
    var vowPath: String? { Bundle.main.object(forInfoDictionaryKey: "VowPath") as? String }

    func applicationDidFinishLaunching(_ notification: Notification) {
        let config = WKWebViewConfiguration()
        config.userContentController.add(self, name: "mori")

        let frame = initialFrame()
        window = PetWindow(contentRect: frame, styleMask: [.borderless], backing: .buffered, defer: false)
        window.isOpaque = false
        window.backgroundColor = .clear
        window.hasShadow = false
        window.level = .floating
        window.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary]
        window.acceptsMouseMovedEvents = true  // hover lean works without focus

        web = PetWebView(frame: NSRect(origin: .zero, size: frame.size), configuration: config)
        web.setValue(false, forKey: "drawsBackground")
        web.autoresizingMask = [.width, .height]
        web.navigationDelegate = self
        window.contentView = web
        if let url = Bundle.main.url(forResource: "pet", withExtension: "html") {
            web.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        window.orderFrontRegardless()

        timer = Timer.scheduledTimer(withTimeInterval: 1.5, repeats: true) { [weak self] _ in
            self?.push(force: false)
        }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        push(force: true)
    }

    // Bottom-right of the main screen, or wherever the user last dropped Mori.
    func initialFrame() -> NSRect {
        let d = UserDefaults.standard
        let screen = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        var maxX = screen.maxX - 24, minY = screen.minY + 24
        if d.object(forKey: "maxX") != nil {
            maxX = CGFloat(d.double(forKey: "maxX"))
            minY = CGFloat(d.double(forKey: "minY"))
        }
        return clamp(NSRect(x: maxX - smallSize.width, y: minY, width: smallSize.width, height: smallSize.height))
    }

    func clamp(_ f: NSRect) -> NSRect {
        let screen = (window?.screen ?? NSScreen.main)?.visibleFrame ?? f
        var r = f
        r.origin.x = min(max(r.origin.x, screen.minX), screen.maxX - r.width)
        r.origin.y = min(max(r.origin.y, screen.minY), screen.maxY - r.height)
        return r
    }

    func push(force: Bool) {
        let json = (try? String(contentsOfFile: statePath, encoding: .utf8)) ?? "null"
        if !force && json == lastJSON { return }
        lastJSON = json
        web.evaluateJavaScript("window.moriUpdate && window.moriUpdate(\(json))", completionHandler: nil)
    }

    func userContentController(_ controller: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let type = body["type"] as? String else { return }
        let num = { (k: String) in CGFloat((body[k] as? NSNumber)?.doubleValue ?? 0) }
        switch type {
        case "resize":
            // Grow up and to the left, keeping Mori's bottom-right corner in place.
            var f = window.frame
            let maxX = f.maxX
            f.size = NSSize(width: num("w"), height: num("h"))
            f.origin.x = maxX - f.width
            window.setFrame(clamp(f), display: true, animate: false)
        case "dragStart":
            dragOrigin = window.frame.origin
        case "drag":
            window.setFrameOrigin(NSPoint(x: dragOrigin.x + num("dx"), y: dragOrigin.y - num("dy")))
        case "dragEnd":
            window.setFrame(clamp(window.frame), display: true)
            UserDefaults.standard.set(Double(window.frame.maxX), forKey: "maxX")
            UserDefaults.standard.set(Double(window.frame.minY), forKey: "minY")
        case "recheck":
            recheck()
        case "menu":
            let menu = NSMenu()
            menu.addItem(withTitle: "Re-check vow", action: #selector(recheck), keyEquivalent: "").target = self
            menu.addItem(.separator())
            menu.addItem(withTitle: "Quit Mori", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
            menu.popUp(positioning: nil, at: window.convertPoint(fromScreen: NSEvent.mouseLocation), in: window.contentView)
        default:
            break
        }
    }

    @objc func recheck() {
        guard let vow = vowPath else { return }
        DispatchQueue.global(qos: .userInitiated).async {
            let p = Process()
            p.executableURL = URL(fileURLWithPath: vow)
            p.arguments = ["check"]
            p.standardOutput = FileHandle.nullDevice
            p.standardError = FileHandle.nullDevice
            try? p.run()
            p.waitUntilExit()
            DispatchQueue.main.async {
                self.push(force: true)
                self.web.evaluateJavaScript("window.moriRecheckDone && window.moriRecheckDone()", completionHandler: nil)
            }
        }
    }
}

let app = NSApplication.shared
let pet = Pet()
app.delegate = pet
app.setActivationPolicy(.accessory)
app.run()
